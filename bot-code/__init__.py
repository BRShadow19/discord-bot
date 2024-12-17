import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os
import itertools
import random

load_dotenv('token.env')    # Load environment variables from token.env
token = os.environ.get('TOKEN')     # The Discord API bot token

import music
import weather
import util
import osu
import league
# Change this when GameAPI is running in a container
GAMEAPI_URL = "http://127.0.0.1:5000"

bot_command_prefix = 'm!'
bot_description = 'A simple music bot'

# Create our bot object
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_command_prefix),
                   description=bot_description, intents=discord.Intents.all())

# Create our client object
client = discord.Client(intents=discord.Intents.all())

#ids for both testing bot and the live bot
bot_ids = [1030504910543912961, 984489028877443103]

#for on_message shenanigans
blackList = ["never"]
shutup = ["stfu", "shut up", "shut the fuck up", "shush", "silence"]
bot_word = ["bot", "mctaco", "mctaco bot", "mctacobot"]
combos = list(itertools.product(shutup, bot_word))
phrases = [" ".join(tup) for tup in combos]

# Print a message to the console when the bot is logged in
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.event
async def on_reaction_add(reaction, user):
    if (not user.bot):
        id = reaction.message.id
        music_cog = bot.get_cog('Music')
        queueID = music_cog.queueEmbed.id
        right_arrow = '➡️'
        left_arrow = '⬅️'
        if id == queueID:
            # Check which arrow
            if str(reaction) == right_arrow:
                # Go right a page
                if music_cog.currentPage < len(music_cog.queuePages)-1:
                    music_cog.currentPage += 1
                    e = discord.Embed(title="__Here's what's in the Queue:__", description=music_cog.queuePages[music_cog.currentPage], color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(music.song_queue)), icon_url=reaction.message.guild.icon).set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
                    await music_cog.queueEmbed.edit(embed=e)
                    await reaction.remove(user)
                else:
                    await reaction.remove(user)
            elif str(reaction) == left_arrow: 
                # Go left a page
                if music_cog.currentPage > 0:
                    music_cog.currentPage -= 1
                    e = discord.Embed(title="__Here's what's in the Queue:__", description=music_cog.queuePages[music_cog.currentPage], color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(music.song_queue)), icon_url=reaction.message.guild.icon).set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
                    await music_cog.queueEmbed.edit(embed=e)
                    await reaction.remove(user)
                else:
                    await reaction.remove(user)

#passive easter eggs :) 
#NOTE : if adding anymore, the return after is needed so it doesn't spam 2-3 of these at once.

#The order that these show up in the code is their priority order as well, 
#so if a message contains both an "er" word and a ":3", it will prioritize the "er"

@bot.event
async def on_message(message):
        
        #preventing it from infinitely replying to its own messages NOTE: ALWAYS first 
        if message.author.id in bot_ids:
            return
        
        #making sure it puts legitimate commands first and does not send any EE message
        await bot.process_commands(message)

        if message.content.startswith(bot_command_prefix):
            return
        
        #making string lowercase + array of each word in message
        lowered = message.content.lower()
        split_str = lowered.split()

        
        #if told to shutup -> replies :(
        for phrase in phrases:
            if lowered.find(phrase) != -1:
                await message.channel.send(":(")
                return
            
        #making string lowercase + array of each word in message
        lowered = message.content.lower()
        split_str = lowered.split()

        #if it finds a word that ends in "er" AND is longer than 4 letter AND is not in the word blacklist-> replies {word}? I hardly know'er!
        for word in split_str:
            if word.endswith("er") and len(word) > 4 and word not in blackList:
                if random.randint(0,1000) < 25:
                    await message.channel.send(word + "? I hardly know'er!")
                return
            
        #:3 -> replies :3
        if ":3" in split_str:
            await message.channel.send(":3") 
            return
      
            
        





# Add new cogs to the bot (link the commands to the bot)
asyncio.run(music.setup(bot))
asyncio.run(weather.setup(bot))
asyncio.run(util.setup(bot))
asyncio.run(osu.setup(bot))
asyncio.run(league.setup(bot, GAMEAPI_URL))

# Start up the bot
bot.run(token)



