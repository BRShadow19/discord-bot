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
  """This class contains all of the music-related commands for the bot
  """
  def __init__(self, bot):
    self.bot = bot
    self.isPlaying = False
    self.currentTitle = ''
    self.skipping = False
    self.lq = False
    self.queueEmbed = None
    self.queuePages = []
    self.currentPage = 0


  @commands.command()
  async def join(self, ctx, *, channel: discord.VoiceChannel):
    """ Makes the bot join or move to the given voice channel
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        channel (discord.VoiceChannel): The name of the channel for the bot to join
    """    
    if ctx.voice_client is not None:
      await ctx.voice_client.move_to(channel)
      await ctx.send('Sliding into {}'.format(channel))
    try:
      await channel.connect()
      await ctx.send('Sliding into {}'.format(channel))
    except Exception:
      await ctx.send('That is not a valid voice channel name!')
    

  @commands.command()
  async def play(self, ctx, *, url=''):
    """Plays a song based on what URL is given. Utilizes link_utils.py to determine the type of link, and then uses
    youtube_dl to search for the song on YouTube. This then creates a YTDLSource object that is used by the bot to be 
    streamed in the voice channel.
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        url (str, optional): URL of a YouTube video or playlist, or a Spotify track or playlist. Can also simply be
          the name of a song/video. Defaults to ''.
    """    
    if len(url) > 0:  # Make sure the user actually gave a URL or song name
      is_playlist = False
      link_type = await link_utils.identify_url(url)  
      if link_type == 'Spotify' or 'Spotify_Playlist':  # Need to convert Spotify links to a searchable YouTube term
        songs = await link_utils.convert_spotify_to_youtube(url)  # List of songs from the Spotify URL (could be just one)
        if len(songs) == 1:
          url = songs[0]
        if len(songs) > 1:
          is_playlist = True
          url = songs[0]

      if link_type == 'YouTube_Playlist':
        is_playlist = True

      if ctx.voice_client.is_playing(): # If nothing is playing right now
        if not is_playlist:
          # Use youtube_dl to search for the video and create a YTDLSource object
          player = await YTDL.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
          song_queue.append(player.title)
          # Send a message of what song was added to the queue, as well as the length of the song
          await ctx.send(':white_check_mark: Now in line -> **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
          await self.whileplaying(ctx)
        else: # The URL is of a playlist
          if link_type == 'Spotify_Playlist':
            await self.playlist(ctx, link_type, songs=songs)  # Add the Spotify songs to the queue
          else:
            await self.playlist(ctx, link_type, url=url)  # Add the YouTube playlist songs to the queue
      else: # Something is currently playing
        if not is_playlist:   
          async with ctx.typing():
            # Use youtube_dl to search for the video and create a YTDLSource object
            player = await YTDL.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            # Send a message of what song was added to the queue, as well as the length of the song
            message = await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
            await asyncio.sleep(10)
            await message.delete()
            self.currentTitle = player.title
        else: # The URL is of a playlist
          if link_type == 'Spotify_Playlist':
            await self.playlist(ctx, link_type, songs=songs)  # Add the Spotify songs to the queue
          else:
            await self.playlist(ctx, link_type, url=url)  # Add the YouTube playlist songs to the queue
    else: # The user did not send a URL or song name
      await ctx.send('To use this command, please enter a song name or url')


  async def whileplaying(self,ctx):
    """ TODO: Devon please document this method since you wrote it, thanks bud 
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    Returns:
        None: If no songs are left in the queue and nothing is playing, this method returns None
    """    
    while len(song_queue) >= 1:
      if ctx.voice_client.is_playing() or self.skipping or ctx.voice_client.is_paused():
        await asyncio.sleep(2)
        while self.lq == True:
          while ctx.voice_client.is_playing():
            await asyncio.sleep(3)
          for songs in islice(cycle(song_queue), len(song_queue) * 100):
            player = await YTDL.YTDLSource.from_url(songs, loop=self.bot.loop, stream=True) 
            ctx.voice_client.play(player)
            message = await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
            await asyncio.sleep(10)
            await message.delete()
            #if ctx.voice_client.is_playing() is None:
            while ctx.voice_client.is_playing() == True:
              await asyncio.sleep(2)
      else:
        try:
          player = await YTDL.YTDLSource.from_url(song_queue[0], loop=self.bot.loop, stream=True)
          ctx.voice_client.play(player)
          song_queue.pop(0)
          message = await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
          await asyncio.sleep(10)
          await message.delete()
          self.currentTitle = player.title
        except TypeError:
          pass
        except UnboundLocalError:
          pass
        except discord.ClientException:
          pass
        except IndexError:
          pass


  @commands.command()
  async def stop(self, ctx):
    """Stops the music that is currently playing (if any) and disconnects the bot from the voice channel
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    if ctx.voice_client:
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
    """Pauses the audio that is currently playing
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    ctx.voice_client.pause()
    await ctx.send('The music is now paused.')


  @commands.command()
  async def leave(self, ctx):
    """Disconnects the bot from the voice channel if it's currently in one
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    if ctx.voice_client is not None:
      await ctx.send('See ya next time')
      await ctx.voice_client.disconnect()
      song_queue.clear()
    else: 
      await ctx.send('Bot is currently not in a voice channel ._.')
  

  @commands.command()
  async def np(self,ctx):
    """Sends a message that says what audio is currently playing (if anything is playing)
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    if ctx.voice_client is None:
      await ctx.send('Not connected to a voice channel')
    if ctx.voice_client and ctx.voice_client.is_playing() == False:
      await ctx.send('Nothing is playing')
    if ctx.voice_client.is_playing():
      await ctx.send(':slight_smile: Now Playing: **{}**'.format(self.currentTitle))


  @commands.command()
  async def duration(self, ctx, player):
    """Sends a message that contains the duration of the current song 
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        player (_type_): _description_
    """    
    # Use the title of the current song to create a new YTDLSource object based on that song
    # This new object will not have been used yet, and thus will have the full duration
    song = await YTDL.YTDLSource.from_url(player.title, loop=self.bot.loop, stream=True)
    
    if song.duration < 60:  # Song is less than a minute
      await ctx.send('{} seconds long'.format(song.duration))

    if song.duration > 60 and song.duration < 3600: # Song is between 1 minute and an hour
      minutes = song.duration//60
      seconds = song.duration%60
      await ctx.send('{} minutes and {} seconds long'.format(minutes, seconds))

    if song.duration >= 3600: # Song is greater than an hour
      hours = song.duration//3600
      seconds = song.duration%3600
      minutes = seconds//60
      seconds = seconds%60
      await ctx.send('{} hours, {} minutes, and {} seconds long'.format(hours, minutes, seconds))


  @commands.command()
  async def resume(self, ctx):
    """Resumes the audio that was previously paused
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    ctx.voice_client.resume()
    await ctx.send('Resuming the music!')

  @commands.command()
  async def isPaused(self, ctx):
    """Check to see if there is any audio that is currently paused
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    if ctx.voice_client.is_paused():
      await ctx.send(':pause_button: **{}** is currently paused.'.format(self.currentTitle))
    else:
      await ctx.send('No music is paused right now.')
  
  
  @commands.command()
  async def queue(self, ctx):
    """Sends a Discord Embed containing all songs that are currently in the queue
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    if len(song_queue) == 0:
      await ctx.send('Nothing in the queue ._.')
    else:
      message = ""
      pages = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
      page = 0
      for i in range(len(song_queue)):
        print(pages[page])
        print(song_queue[i])
        print(page)
        if len(pages[page] + (str(i+1) + ". " + song_queue[i] + "\n")) < 4000:
          pages[page] += (str(i+1) + ". " + song_queue[i] + "\n")
        else:
          page += 1
          pages[page] += (str(i+1) + ". " + song_queue[i] + "\n")
        message += (str(i+1) + ". " + song_queue[i] + "\n")

      e = discord.Embed(title="__Here's what's in the Queue:__", description=pages[0], color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(song_queue)), icon_url='https://i.ytimg.com/vi/YNopLDl2OHc/hqdefault.jpg').set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
      msg = await ctx.send(embed=e)
      self.queueEmbed = msg
      self.queuePages = pages
      self.currentPage = 0


  @commands.command()
  async def loop(self,ctx):
    """Has the bot loop (repeat) the queue indefinitely
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    

    if len(song_queue) == 0:
      return await ctx.send("Nothing inside the queue to loop o.o")
    if len(song_queue) > 0:
      song_queue.append(self.currentTitle)  # Add the current song back to the end of the queue, otherwise this one will not be repeated
      if self.lq == True:
        await ctx.send(":repeat: Stopping repeat")
        self.lq = False
      else:
        self.lq = True
        await ctx.send(":repeat: Queue is being `looped!`")


  @commands.command()
  async def clear(self,ctx):
    """Clears all songs from the queue
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    self.lq == False
    if len(song_queue) == 0:
      await ctx.send('Nothing to clear..')
    else:
      song_queue.clear()
      await ctx.send("Queue has been cleared!")


  @commands.command()
  async def skip(self, ctx):
    """Skip the song that is currently playing. If there is nothing playing, alert the user. If the queue is empty, stop the audio.
    If there are other songs in the queue, play the next one and remove it (or add to the end if )
    Args:
        ctx (_type_): _description_
    """    
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
    """Shuffle the songs that are in the queue
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    """    
    rand.shuffle(song_queue)
    await ctx.send(":twisted_rightwards_arrows: The queue has been shuffled!")
    await self.queue(ctx) # Show the user what the shuffled queue is

  
  async def playlist(self, ctx, link_type, *, url='', songs=[]):
    """Adds all the songs from a playlist to the queue
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        url (str or list): URL of a YouTube or Spotify playlist
        link_type (str): Says whether the link is for a YouTube playlist, or a Spotify playlist
    """    
    await ctx.send(':musical_note: Gathering playlist, please hold :musical_note:')
    if link_type == link_utils.LinkType.Spotify_Playlist:
      for song in songs:  
        song_queue.append(song)
      await ctx.send("{} songs have been added to the queue!".format(len(songs)))

    elif link_type == link_utils.LinkType.YouTube_Playlist:
      playlist = pafy.get_playlist2(url)
      for song in playlist:
        title = song.title
        song_queue.append(title)
      await ctx.send("{} songs have been added to the queue!".format(len(playlist)))

    await self.ensure_voice(ctx)
    if not ctx.voice_client.is_playing():
      player = await YTDL.YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player)
      message = await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
      self.currentTitle = player.title
      await asyncio.sleep(10)
      await message.delete()
      await self.whileplaying(ctx)
    else:
      await self.whileplaying(ctx)


  """
  @commands.command()
  async def embed(self, ctx, content):
    e = discord.Embed(title="Test", description=content, color=discord.Color.blue())
    await ctx.send(embed=e)
  """

  @skip.before_invoke
  async def ensure_skip(self, ctx):
    """Sets the self.skipping variable to True, which locks out the whilePlaying method from moving to the next song.
    This method is required in order to prevent a rare error when a user sends the skip command at the same time as when
    the whilePlaying method is trying to start the next song.
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
          This arg is only here because this method needs the same required parameters as the skip method
    """    
    self.skipping = True
    await asyncio.sleep(1)


  @play.before_invoke
  async def ensure_voice(self, ctx):
    """Ensures that the bot is in a voice channel before executing the play command.
    Args:
        ctx (Obj): Object containing all information about the context of the bot within a Discord server,
          such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
    Raises:
        commands.CommandError: If the user who sent the play command is not in a voice channel, this will prevent the 
        play command from executing
    """    
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("You are not connected to a voice channel.")
        raise commands.CommandError("Author not connected to a voice channel.")


async def setup(bot):
  """Adds this cog to the bot, meaning that the commands in the Music class can be used by the bot/users
    Args:
        bot (discord.Bot): The bot object to have the cog added to
    """    
  global pafy_key
  pafy_key = os.environ.get('KEY')
  pafy.set_api_key(pafy_key)
  await bot.add_cog(Music(bot))
  print("Music is online!")