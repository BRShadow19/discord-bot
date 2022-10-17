import asyncio
import pafy
import discord
import os
from discord.ext import commands
import random as rand
from itertools import cycle, islice
import YTDLSource as YTDL
import link_utils
import datetime
import random
import pytz

class Utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.answers = ["It is certain", "Outlook good", "You may rely on it ", "Ask again later", 
        "Concentrate and ask again", "Reply hazy, try again", "My reply is no", "My sources say no"]
        self.jokes = ["give me jokes to add please im begging you"]
        
    @commands.command()
    async def list(self, ctx, *,type = ''):
        """Sends a Discord Embed containing the list of all music commands

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
            such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        """    
        if(len(type) == 0):
            await ctx.reply('m!list options are `weather` `music` `general`' 
                            +'\nexample: `m!list music`')
        else:
            type.lower()
            general_desc = str('\n`m!list [type]:` Gives a list of commands for the given type' 
            + '\n`m!time:` Tells the time where the bot is hosted'
            + '\n`m!8ball [question]:` Gives an 8ball answer to a yes or no question'
            + '\n`m!joke:` Tells a joke'
            + '\n`m!coinflip:` Flips a coin')
            
            osu_desc = str('soon :copium:')

            overwatch_desc = str('soon :copium:')

            league_desc = str('soon :copium:')

            weather_desc = str('\n`m!weather [City]:` Shows the current weather at the given city'
            +'\n`m!forecast [City]:` Shows the 6-day forecast of the given city')
            
            music_desc = str('\n`m!join:` Puts the bot in your voice channel'
            +'\n`m!play:`Play a song or playlist from YouTube or Spotify'
            +'\n`m!pause:` Pause the current song'
            +'\n`m!resume:` Resume the paused song'
            +'\n`m!stop:` Stops playing music'
            +'\n`m!leave:` Bot leaves the voice channel'
            +'\n`m!queue:` See a list of songs in the queue'
            +'\n`m!skip:` Skips the current song'
            +'\n`m!shuffle:` Shuffles the queue'
            +'\n`m!clear:` Clears the queue' 
            +'\n`m!np:` Displays the current song')
            help_dictionary = {'general': general_desc, 'osu': osu_desc, 'overwatch': overwatch_desc, 
                                'league': league_desc, 'weather': weather_desc, 'music': music_desc}
            if(not type in help_dictionary.keys()):
                await ctx.reply('m!list options are `weather` `music` `general`' 
                            +'\nexample: `m!list music`')
            else:
                e = discord.Embed(title="__List of Commands:__", description=help_dictionary[type], color=discord.Color.blue()). set_thumbnail(url='https://i.imgur.com/txfgXAE.png')
                await ctx.reply(embed=e)

    @commands.command()
    async def time(self,ctx):
        """Sends a message telling the current time (based on where the bot host is located)

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        """
        current_time = datetime.datetime.now()
        await ctx.send(":clock2: *{}*".format(current_time.astimezone(pytz.timezone('US/Eastern')).strftime("%I:%M %p on %A, %b %d")))
    
    @commands.command(name = '8ball')
    async def _8ball(self, ctx, *,question = ''):
        index = random.randint(0, len(self.answers) - 1)
        await ctx.reply(self.answers[index])

    @commands.command()
    async def coinflip(self, ctx):
        num = random.randint(1,2)
        if(num == 1):
            await ctx.reply('Heads')
        elif(num == 2):
            await ctx.reply('Tails')

    @commands.command()
    async def joke(self, ctx):
        index = random.randint(0, len(self.jokes) - 1)
        await ctx.reply(self.jokes[index])

async def setup(bot):
    """Adds this cog to the bot, meaning that the commands in the Utils class can be used by the bot/users

    Args:
        bot (discord.Bot): The bot object to have the cog added to
    """    
    await bot.add_cog(Utils(bot))
    print("Util is online!")
        
