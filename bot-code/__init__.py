import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os

load_dotenv('token.env')    # Load environment variables from token.env
token = os.environ.get('TOKEN')     # The Discord API bot token

import music
import weather

bot_command_prefix = 'm!'
bot_description = 'A simple music bot'

# Create our bot object
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_command_prefix),
                   description=bot_description, intents=discord.Intents.all())

# Print a message to the console when the bot is logged in
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

# Add new cogs to the bot (link the commands to the bot)
asyncio.run(music.setup(bot))
asyncio.run(weather.setup(bot))

# Start up the bot
bot.run(token)



