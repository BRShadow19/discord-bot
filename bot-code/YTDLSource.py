import discord
import asyncio
import logging
import threading
import time
import yt_dlp

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda *args, **kwargs: ''

log = logging.getLogger('musicbot.audio')

FRAME_SECONDS = 0.02        # discord.py pulls 20 ms of PCM per read()
SLOW_READ_SECONDS = 1.0     # log reads that block at least this long
STALL_WARN_SECONDS = 5.0    # warn while a read is still blocked after this long

ffmpeg_options = {
    'options': '-vn',
    # -rw_timeout (microseconds): give up on a socket that has gone silent after 10 s instead
    # of blocking forever. With -reconnect, ffmpeg then resumes from the current byte offset.
    # Do NOT add -reconnect_at_eof: in testing it made ffmpeg retry at the real end of every
    # track (~8 s delay plus an I/O error).
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -rw_timeout 10000000'
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'youtube_include_dash-manifest': False
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class InstrumentedFFmpegPCMAudio(discord.FFmpegPCMAudio):
    """FFmpegPCMAudio that logs how playback ended. Logging only; playback is unchanged.

    Separates three cases that all look like "audio stopped" from the outside:
      - a hung read: ffmpeg is alive but has stopped producing audio (watchdog warning)
      - ffmpeg ending on its own before the expected duration (hit_eof=True, played < expected)
      - playback stopped or skipped by a user (hit_eof=False, ffmpeg_rc=None)
    """

    def __init__(self, source, *, label='?', expected_duration=None, **kwargs):
        super().__init__(source, **kwargs)
        self.label = label
        self.expected_duration = expected_duration
        self.frames = 0
        self.slow_reads = 0
        self.longest_read = 0.0
        self._read_started = None       # monotonic time while a read() is in progress
        self._stall_logged = False
        self._hit_eof = False
        self._summarized = False
        self._done = threading.Event()
        log.info('ffmpeg started for %r (pid=%s, expected %ss)', label, self._pid(), expected_duration)
        threading.Thread(target=self._watchdog, name='audio-watchdog', daemon=True).start()

    def _pid(self):
        return getattr(getattr(self, '_process', None), 'pid', None)

    def _returncode(self, wait=0.0):
        """ffmpeg's exit code, or None if it is still running (or already cleaned up)."""
        proc = getattr(self, '_process', None)
        poll = getattr(proc, 'poll', None)
        if poll is None:
            return None
        if wait:
            try:
                proc.wait(timeout=wait)
            except Exception:
                pass
        return poll()

    def read(self):
        started = self._read_started = time.monotonic()
        try:
            data = super().read()
        finally:
            self._read_started = None
        elapsed = time.monotonic() - started
        self.longest_read = max(self.longest_read, elapsed)
        if elapsed >= SLOW_READ_SECONDS:
            self.slow_reads += 1
            log.warning('slow ffmpeg read: %.1fs at %.1fs into %r', elapsed, self.frames * FRAME_SECONDS, self.label)
        if data:
            self.frames += 1
        else:
            self._hit_eof = True
        return data

    def _watchdog(self):
        # A read that never returns can't log for itself, so watch it from a second thread.
        while not self._done.wait(1.0):
            started = self._read_started
            if started is None:
                self._stall_logged = False
                continue
            blocked = time.monotonic() - started
            if blocked >= STALL_WARN_SECONDS and not self._stall_logged:
                self._stall_logged = True
                log.warning('ffmpeg read blocked for %.1fs at %.1fs into %r (pid=%s, ffmpeg exited=%s)',
                            blocked, self.frames * FRAME_SECONDS, self.label, self._pid(),
                            self._returncode() is not None)

    def cleanup(self):
        # discord.py also calls cleanup() from __del__, so only summarize once.
        if getattr(self, '_summarized', True) is False:
            self._summarized = True
            # If ffmpeg ended on its own, give it a moment to exit so the return code is meaningful.
            rc = self._returncode(wait=1.0 if self._hit_eof else 0.0)
            played = self.frames * FRAME_SECONDS
            early = self.expected_duration is not None and played < self.expected_duration - 3
            level = logging.WARNING if (early and self._hit_eof) else logging.INFO
            log.log(level, 'playback ended: %r played=%.1fs expected=%ss hit_eof=%s ffmpeg_rc=%s '
                           'slow_reads=%d longest_read=%.1fs', self.label, played, self.expected_duration,
                    self._hit_eof, rc, self.slow_reads, self.longest_read)
        done = getattr(self, '_done', None)
        if done is not None:
            done.set()
        super().cleanup()


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.is_whileplaying = False
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        source = InstrumentedFFmpegPCMAudio(filename, label=data.get('title'),
                                            expected_duration=data.get('duration'), **ffmpeg_options)
        return cls(source, data=data)