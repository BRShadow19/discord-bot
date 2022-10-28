import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os

load_dotenv('token.env')    # Load environment variables from token.env
token = os.environ.get('TOKEN')     # The Discord API bot token

import music
import weather
import util
import osu

bot_command_prefix = 'm?'
bot_description = 'A simple music bot'

# Create our bot object
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_command_prefix),
                   description=bot_description, intents=discord.Intents.all())

# Print a message to the console when the bot is logged in
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.event
async def on_reaction_add(reaction, user):
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
                    e = discord.Embed(title="__Here's what's in the Queue:__", description=music_cog.queuePages[music_cog.currentPage], color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(music.song_queue)), icon_url='https://i.ytimg.com/vi/YNopLDl2OHc/hqdefault.jpg').set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
                    await music_cog.queueEmbed.edit(embed=e)
                    await reaction.remove(user)
                else:
                    await reaction.remove(user)
            elif str(reaction) == left_arrow: 
                # Go left a page
                if music_cog.currentPage > 0:
                    music_cog.currentPage -= 1
                    e = discord.Embed(title="__Here's what's in the Queue:__", description=music_cog.queuePages[music_cog.currentPage], color=discord.Color.orange()).set_footer(text='{} song(s) in line'.format(len(music.song_queue)), icon_url='https://i.ytimg.com/vi/YNopLDl2OHc/hqdefault.jpg').set_thumbnail(url='https://i.imgur.com/Gu8wmb0.png')
                    await music_cog.queueEmbed.edit(embed=e)
                    await reaction.remove(user)
                else:
                    await reaction.remove(user)


# Add new cogs to the bot (link the commands to the bot)
asyncio.run(music.setup(bot))
asyncio.run(weather.setup(bot))
asyncio.run(util.setup(bot))
asyncio.run(osu.setup(bot))

# Start up the bot
bot.run(token)



