from discord.ext import commands
from dotenv import load_dotenv
import os
import music
import weather

load_dotenv('token.env')
token = os.environ.get('TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or("m!"),
                   description='Simple music bot')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


music.setup(bot)
weather.setup(bot)
bot.run(token)



