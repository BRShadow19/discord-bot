import asyncio
import pafy
import discord
import os
from discord.ext import commands
import random as rand
from itertools import cycle, islice
import YTDLSource as YTDL
import link_utils
song_queue = []
pafy_key = ''

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.isPlaying = False
    self.currentTitle = ''
    self.skipping = False
    self.lq = False

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
  async def play(self, ctx, *, url=''):
    if len(url) > 0:
      player = await YTDL.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      is_playlist = self.isPlaylist(url)
      if ctx.voice_client.is_playing():
        if not is_playlist:
          song_queue.append(player.title)
          await ctx.send(':white_check_mark: Now in line -> **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
          await self.whileplaying(ctx)
        else:
          await self.playlist(ctx, url)
      else:
        if not is_playlist:   
          async with ctx.typing():
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
            self.currentTitle = player.title
        else:
          await self.playlist(ctx, url)
    else:
      await ctx.send('To use this command, please enter a song name or url')

  def isPlaylist(self, url):
    ret = False
    try:
      playlist = pafy.get_playlist2(url)
      ret = True
    except(ValueError):
      pass
    except(TypeError):
      pass
    finally:
      return ret

  async def whileplaying(self,ctx):
    while len(song_queue) >= 1:
      if ctx.voice_client.is_playing() or self.skipping or ctx.voice_client.is_paused():
        await asyncio.sleep(3)
        while self.lq == True:
          while ctx.voice_client.is_playing():
            await asyncio.sleep(2)
          for songs in islice(cycle(song_queue), len(song_queue) * 100):
            try:
              player = await YTDL.YTDLSource.from_url(songs, loop=self.bot.loop, stream=True) 
              ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
              await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
            except (AttributeError):
              pass
            except (TypeError):
              pass
            except (UnboundLocalError):
              pass
            except (discord.errors.ClientException):
              pass
            finally:
              if ctx.voice_client.is_playing() is None:
                while ctx.voice_client.is_playing() == True:
                  await asyncio.sleep(2)
              else:
                return None
      else:
        player = await YTDL.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player)
        await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
        self.currentTitle = player.title

  @commands.command()
  async def stop(self, ctx):
    if ctx.voice_client:
      """Stops and disconnects the bot from voice"""
      if ctx.voice_client.is_playing() == False:
        await ctx.send(':person_facepalming: No music to stop lol')
      else:
        await ctx.voice_client.disconnect()
        await ctx.send('Bye Bye :wave:')
        song_queue.clear()
        self.lq = False
    else:
      await ctx.reply(':person_facepalming: No music to stop lol')
    
  @commands.command()
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send('The music is now paused.')

  @commands.command()
  async def leave(self, ctx):
      if ctx.voice_client is not None:
        await ctx.send('See ya next time')
        ctx.voice_client.disconnect()
      else: 
        await ctx.send('Bot is currently not in a voice channel ._.')
  
  @commands.command()
  async def np(self,ctx):
    if ctx.voice_client is None:
      await ctx.send('Not connected to a voice channel')
    if ctx.voice_client and ctx.voice_client.is_playing() == False:
      await ctx.send('Nothing is playing')
    if ctx.voice_client.is_playing():
      await ctx.send(':slight_smile: Now Playing: **{}**'.format(self.currentTitle))

  @commands.command()
  async def duration(self, ctx, player):
    song = await YTDL.YTDLSource.from_url(player.title, loop=self.bot.loop, stream=True)
    if song.duration < 60:
      await ctx.send('{} seconds long'.format(song.duration))
    if song.duration > 60 and song.duration < 3600:
      minutes = song.duration//60
      seconds = song.duration%60
      await ctx.send('{} minutes and {} seconds long'.format(minutes, seconds))
    if song.duration >= 3600:
      hours = song.duration//3600
      seconds = song.duration%3600
      minutes = seconds//60
      seconds = seconds%60
      await ctx.send('{} hours, {} minutes, and {} seconds long'.format(hours, minutes, seconds))

  @commands.command()
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.send('Resuming the music!')

  @commands.command()
  async def isPaused(self, ctx):
    if ctx.voice_client.is_paused():
      await ctx.send(':pause_button: **{}** is currently paused.'.format(self.currentTitle))
    else:
      await ctx.send('No music is paused right now.')

  @commands.command()
  async def list(self, ctx):
    desc = str('\n`m!join:` Puts the bot in your voice channel'
    +'\n`m!play:`Play a song or playlist from YouTube'
    +'\n`m!pause:` Pause the current song'
    +'\n`m!resume:` Resume the paused song'
    +'\n`m!stop:` Stops playing music'
    +'\n`m!leave:` Bot leaves the voice channel'
    +'\n`m!queue:` See a list of songs in the queue'
    +'\n`m!skip:` Skips the current song'
    +'\n`m!shuffle:` Shuffles the queue'
    +'\n`m!clear:` Clears the queue' 
    +'\n`m!np:` Displays the current song')
    e = discord.Embed(title="__List of Commands:__", description=desc, color=discord.Color.blue()). set_thumbnail(url='https://i.imgur.com/txfgXAE.png')
    await ctx.reply(embed=e)

  @commands.command()
  async def queue(self, ctx):
    if len(song_queue) == 0:
      await ctx.send('Nothing in the queue ._.')
    else:
      #await ctx.send('Heres whats in the Queue:')
      message = ""
      for i in range(len(song_queue)):
        message += (str(i+1) + ". " + song_queue[i] + "\n")
        e = discord.Embed(title="__Here's what's in the Queue:__", description=message, color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(song_queue)), icon_url='https://i.ytimg.com/vi/YNopLDl2OHc/hqdefault.jpg').set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
      await ctx.send(embed=e)

  @commands.command()
  async def loop(self,ctx):
    song_queue.append(self.currentTitle)
    if len(song_queue) > 0:
      if self.lq == True:
        await ctx.send(":repeat: Stopping repeat")
        self.lq = False
      else:
        await ctx.send(":repeat: Queue is being `looped!`")
        self.lq = True
    else:
      await ctx.send("Nothing inside the queue to loop")

  @commands.command()
  async def clear(self,ctx):
    self.lq == False
    if len(song_queue) == 0:
      await ctx.send('Nothing to clear..')
    else:
      song_queue.clear()
      await ctx.send("Queue has been cleared!")

  @commands.command()
  async def skip(self, ctx):
    if ctx.voice_client.is_playing() == False:
      await ctx.send('Nothing is playing..')
    if len(song_queue) == 0:
      if ctx.voice_client.is_playing():
        await asyncio.sleep(1)
        ctx.voice_client.stop()
        await ctx.send('Stopping the audio!'.format(self.currentTitle))
    if len(song_queue) >= 1:
      ctx.voice_client.stop()
      await ctx.send(':track_next: Skipping song :track_next: please hold :track_next:')
      player = await YTDL.YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player)
      await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
    self.skipping = False

  @commands.command()
  async def shuffle(self, ctx):
    rand.shuffle(song_queue)
    await ctx.send(":twisted_rightwards_arrows: The queue has been shuffled!")
    await self.queue(ctx)

  
  async def playlist(self, ctx, url):
    playlist = pafy.get_playlist2(url)
    for song in playlist:
      title = song.title
      song_queue.append(title)
    await ctx.send("{} songs have been added to the queue!".format(len(playlist)))
    await self.ensure_voice(ctx)
    if not ctx.voice_client.is_playing():
      player = await YTDL.YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player)
      await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
      await self.duration(ctx,player)
      self.currentTitle = player.title
      await self.whileplaying(ctx)


  """
  @commands.command()
  async def embed(self, ctx, content):
    e = discord.Embed(title="Test", description=content, color=discord.Color.blue())
    await ctx.send(embed=e)
  """

  @skip.before_invoke
  async def ensure_skip(self, ctx):
    self.skipping = True
    await asyncio.sleep(1)

  @play.before_invoke
  async def ensure_voice(self, ctx):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("You are not connected to a voice channel.")
        raise commands.CommandError("Author not connected to a voice channel.")

def setup(bot):
  global pafy_key
  pafy_key = os.environ.get('KEY')
  pafy.set_api_key(pafy_key)
  bot.add_cog(Music(bot))
  print("Music is online!")