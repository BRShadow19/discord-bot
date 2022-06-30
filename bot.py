import asyncio
from attr import NOTHING
import pafy
import discord
import os
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
import random as rand
song_queue = []
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

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

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Bot token that connects us to the Discord API
load_dotenv('token.env')
token = os.environ.get('TOKEN')
pafy_key = os.environ.get('KEY')
bot = commands.Bot(command_prefix=commands.when_mentioned_or("m!"),
                   description='Simple music bot')

#OBJECTS
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.isPlaying = False
    self.currentTitle = ''

  @commands.command()
  async def join(self, ctx, *, channel: discord.VoiceChannel):
      """Joins a voice channel"""

      if ctx.voice_client is not None:
          await ctx.voice_client.move_to(channel)
          await ctx.send('Sliding into {}'.format(channel))
      try:
        await channel.connect()
        await ctx.send('Sliding into {}'.format(channel))
      except Exception:
        pass
    
  @commands.command()
  async def play(self, ctx, *, url):
    if ctx.voice_client.is_playing():
      async with ctx.typing():
        playerqueue = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        song_queue.append(playerqueue.title)
        await ctx.send('up next: {}'.format(playerqueue.title))
        await self.whileplaying(ctx, playerqueue)
    else:
      async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))
        self.currentTitle = player.title

  @commands.command()
  async def whileplaying(self,ctx, playerqueue):
    while len(song_queue) >= 1:
      if ctx.voice_client.is_playing():
        await asyncio.sleep(5)
      else:
        playerqueue = await YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
        ctx.voice_client.play(playerqueue, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('up next: {}'.format(playerqueue.title))

  @commands.command()
  async def stop(self, ctx):
    """Stops and disconnects the bot from voice"""
    if ctx.voice_client.is_playing() == False:
      await ctx.send('No music to stop lol')
    else:
      ctx.voice_client.stop()
      await ctx.send('Music has stopped playing')
    
  @commands.command()
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send('The music is now paused.')

  @commands.command()
  async def leave(self, ctx):
      if ctx.voice_client is not None:
        await ctx.send('See ya next time')
        await ctx.voice_client.disconnect()
      else: 
        await ctx.send('Bot is currently not in a voice channel')

  @commands.command()
  async def duration(self, ctx, *, url):
    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
    await ctx.send('This is song is: {} minutes long'.format(player.duration/60))

  @commands.command()
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.send('Resuming the music!')

  @commands.command()
  async def isPaused(self, ctx):
    if ctx.voice_client.is_paused():
      await ctx.send('{} is currently paused.'.format(self.currentTitle))
    else:
      await ctx.send('No music is paused right now.')

  @commands.command()
  async def commandlist(self, ctx):
    await ctx.send('Commands:'+
    '\nm!join: Puts the bot in your voice channel'+
    '\nm!play: plays music'+
    '\nm!stop: stops playing music'+
    '\nm!resume: resumes music'+
    '\nm!leave: Bot leaves'+
    '\nm!queue: see whats in the queue'+
    '\nm!skip: skips current song'+
    '\nm!playlist: You can add a YouTube playlist full of songs'+
    '\nm!shuffle: Shuffles the playlist'+
    '\nm!clear: Clears the playlist')

  @commands.command()
  async def queue(self, ctx):
    if len(song_queue) == 0:
      await ctx.send('Nothing in the queue')
    else:
      await ctx.send('Heres whats in the Queue:')
      message = ""
      for x in song_queue:
        message += (x + "\n")
      await ctx.send(message)

  @commands.command()
  async def clear(self,ctx):
    if len(song_queue) == 0:
      await ctx.send('Nothing to clear')
    else:
      song_queue.clear()
      await ctx.send("queue has been cleared")

  @commands.command()
  async def skip(self, ctx):
    if len(song_queue) >= 1:
      ctx.voice_client.stop()
      player = await YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player)
      await ctx.send('Now playing: {}'.format(player.title))
    else:
      await ctx.send('Nothing to skip lol')

  @commands.command()
  async def shuffle(self, ctx):
    rand.shuffle(song_queue)
    await ctx.send("The queue has been shuffled!")
    await self.queue(ctx)

  @commands.command()
  async def playlist(self, ctx, *, url):
    pafy.set_api_key(pafy_key)
    playlist = pafy.get_playlist2(url)
    for song in playlist:
      title = song.title
      song_queue.append(title)
    await ctx.send("{} songs have been added to the queue!".format(len(playlist)))


  @play.before_invoke
  async def ensure_voice(self, ctx):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("You are not connected to a voice channel.")
        raise commands.CommandError("Author not connected to a voice channel.")

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(token)