import requests
import asyncio
import pafy
import discord
import os
from discord.ext import commands
API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'http://osu.ppy.sh/oauth/token'

class osu(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    async def get_token(self):
        data = {
            'client_id' : os.environ.get('OSU_ID'),
            'client_secret' : os.environ.get('OSU'),
            'grant_type' : 'client_credentials',
            'scope' : 'public'
        }
        
        response = requests.post(TOKEN_URL, data=data)

        return response.json().get('access_token')

    async def get_header(self):
        token = await self.get_token()
        headers = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }

        return headers

    async def get_param(self):
        params = {
            'mode' : 'osu',
            'limit' : 5
        }
        return params
    async def get_userid(self, username):
        params= await self.get_param()
        headers= await self.get_header()
        data = requests.get(f'{API_URL}/users/{username}', params = params,  headers = headers)
        return str(data.json().get('id'))


    @commands.command()
    async def top(self, ctx, username=''):
        params= await self.get_param()
        headers= await self.get_header()
        #data = requests.get(f'{API_URL}/users/{username}', params = params,  headers = headers)
        id = await self.get_userid(username)
        response = requests.get(f'{API_URL}/users/{id}/scores/best', params=params, headers=headers)
        performance_stat = ''
        map_stat = ''
        pp_stat = 'pp : ' + str(round(response.json()[0].get('pp')))
        
        
        performance_stat += pp_stat
        await ctx.send(performance_stat)

async def setup(bot):
  """Adds this cog to the bot, meaning that the commands in the osu class can be used by the bot/users

    Args:
        bot (discord.Bot): The bot object to have the cog added to
    """    
  global pafy_key
  pafy_key = os.environ.get('KEY')
  pafy.set_api_key(pafy_key)
  await bot.add_cog(osu(bot))
  print("osu! is online!")

