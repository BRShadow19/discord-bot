import asyncio
from msilib.schema import LaunchCondition
import pafy
import discord
import os
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
import random as rand
from itertools import cycle, islice
import requests, json
import datetime
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
weather_key = os.environ.get('WEA')
pafy.set_api_key(pafy_key)
bot = commands.Bot(command_prefix=commands.when_mentioned_or("m!"),
                   description='Simple music bot')

#OBJECTS
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

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
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
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
              player = await YTDLSource.from_url(songs, loop=self.bot.loop, stream=True) 
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
        player = await YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
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
    song = await YTDLSource.from_url(player.title, loop=self.bot.loop, stream=True)
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
      player = await YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player)
      await ctx.send(':notes: Now playing: **{}** *({} minutes and {} seconds long)*'.format(player.title, player.duration//60, player.duration%60))
    self.skipping = False

  @commands.command()
  async def shuffle(self, ctx):
    rand.shuffle(song_queue)
    await ctx.send(":twisted_rightwards_arrows: The queue has been shuffled!")
    await self.queue(ctx)

  @commands.command()
  async def weather(self,ctx,city='',city_second_space='',city_third_space=''):
    current_city = str(city) + " " + str(city_second_space) + " " + city_third_space
    if city == '' or city is None:
        await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
        return None
    complete_url = "http://api.openweathermap.org/data/2.5/weather?" + "appid=" + weather_key + "&q=" + current_city + "&units=imperial"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        opendata = data["main"]
        temp = opendata["temp"]
        temp_max = opendata["temp_max"]
        temp_min = opendata["temp_min"]
        humidity = opendata["humidity"]
        weather = data["weather"]
        desc = weather[0]["description"]
        g = discord.Embed(title=":white_sun_cloud: _**{}**_:thunder_cloud_rain:".format(current_city), description="High: *{}°*, low: *{}°*\nCurrent Temp: **{}°**\nHumidity: {}\nDescription: {}".format(str(temp_max), str(temp_min), str(temp), str(humidity), str(desc)), color=discord.Color.dark_blue()).set_footer(text='For a forecast 5 days in advance -> m!forecast', icon_url='https://i.imgur.com/oWQeUDj.png')
        await ctx.send(embed=g)
    else:
        await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

  @commands.command()
  async def forecast(self,ctx,city='',city_second_space='',city_third_space=''):
    current_city = str(city) + " " + str(city_second_space) + " " + city_third_space
    if city == '' or city is None:
        await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
        return None
    lonLatCall = "http://api.openweathermap.org/geo/1.0/direct?" +"q=" + current_city + "&appid=" + weather_key
    response = requests.get(lonLatCall)
    data_first_call = response.json()
    lon = data_first_call[0]["lon"]
    lat = data_first_call[0]["lat"]
    latt = str(lat)
    lonn = str(lon)
    forecast_call = "http://api.openweathermap.org/data/2.5/forecast?" + "appid=" + weather_key + "&lat=" + latt + "&lon=" + lonn + "&units=imperial"
    forecast_response = requests.get(forecast_call)
    for_data = forecast_response.json()
    if for_data["cod"] != "404":
      forecast = for_data["list"]
      temp = ""
      tomorrow = datetime.date.today() + datetime.timedelta(days=1)
      for x in range(6):
        temp += "**{}**\n:thermometer:High: {} - Low: {} - Avg: **{}**°\n sky: *{}*\n\n".format(tomorrow + datetime.timedelta(days=x), forecast[x]["main"]["temp_max"], forecast[x]["main"]["temp_min"], forecast[x]["main"]["temp"], forecast[x]["weather"][0]["description"])
      g = discord.Embed(title=":white_sun_cloud: _**{}**_'s Expected Weather (Next 6 days) :thunder_cloud_rain:".format(current_city.capitalize()), description=temp, color=discord.Color.dark_blue()).set_footer(text='Want the current temperature? use m!weather', icon_url='https://i.imgur.com/oWQeUDj.png').set_thumbnail(url='https://i.imgur.com/j7WQ7bx.png')
      await ctx.send(embed=g)
    else:
        await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

  @commands.command()
  async def time(self,ctx):
    await ctx.send(":clock2: *{}*".format(datetime.datetime.now().strftime("%I:%M %p on %A, %b %d")))

  async def playlist(self, ctx, url):
    playlist = pafy.get_playlist2(url)
    for song in playlist:
      title = song.title
      song_queue.append(title)
    await ctx.send("{} songs have been added to the queue!".format(len(playlist)))
    await self.ensure_voice(ctx)
    if not ctx.voice_client.is_playing():
      player = await YTDLSource.from_url(song_queue.pop(0), loop=self.bot.loop, stream=True)
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

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))
bot.run(token)