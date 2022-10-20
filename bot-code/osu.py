import requests
import asyncio
import pafy
import discord
import os
import math
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
    #retrieves header dictionary
    async def get_header(self):
        token = await self.get_token()
        headers = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }

        return headers
    #retrieves params dictionary
    async def get_param(self):
        params = {
            'mode' : 'osu',
            'limit' : 5
        }
        return params

    #changes params dictionary, used if user wants to look at a different mode or a different number of plays
    async def change_param(self, mode, limit):
        params = {
            'mode' : mode,
            'limit' : limit
        }
        return params
    
    #retrieves the users account ID from their username
    async def get_userid(self, username):
        params= await self.get_param()
        headers= await self.get_header()
        data = requests.get(f'{API_URL}/users/{username}', params = params,  headers = headers)
        return str(data.json().get('id'))

    #gives a list of the users top 5 pp plays 
    @commands.command()
    async def top(self, ctx, username=''):
        params= await self.get_param()
        headers= await self.get_header()
        id = await self.get_userid(username)
        response = requests.get(f'{API_URL}/users/{id}/scores/best', params=params, headers=headers)
        performance_stat = ''
        n = params.get('limit')
        for i in range(0, n):
            pp_stat = str(round(response.json()[i].get('pp'), 2))
            map_name = response.json()[i].get('beatmapset')['title']
            diff_name = response.json()[i].get('beatmap')['version']
            acc_stat = str(round(response.json()[i].get('accuracy') * 100, 2))
            rank = response.json()[i].get('rank')
            count_300 = str(response.json()[i].get('statistics')['count_300'])
            count_100 = str(response.json()[i].get('statistics')['count_100'])
            count_50 = str(response.json()[i].get('statistics')['count_50'])
            performance_stat += str(str(i + 1) + ') ' + pp_stat + 'pp' + '\n'
                             + map_name + ' [' + diff_name + ']' '\n'
                             + acc_stat + '%' + '\n'
                             + rank + '\n'
                             + count_300 + '/' + count_100 + '/' + count_50 + '\n')
                        
      
        await ctx.send(performance_stat)

    #gives the given users most recent play
    @commands.command(name = 'rs')
    async def recent(self, ctx, username = ''):
        params= await self.get_param()
        headers= await self.get_header()
        id = await self.get_userid(username)
        response = requests.get(f'{API_URL}/users/{id}/scores/recent?include_fails=1', params=params, headers=headers)
        output= ''
        if(len(response.json()) == 0):
            output += 'No recent plays from `' + username + '`'
        elif(not response.json()[0].get('passed')):
            output += 'i currently dont know how to get some stats to show up if you failed so take this : **L**'
        else:
            pp_stat = str(round(response.json()[0].get('pp'), 2))
            map_name = response.json()[0].get('beatmapset')['title']
            diff_name = response.json()[0].get('beatmap')['version']
            acc_stat = str(round(response.json()[0].get('accuracy') * 100, 2))
            rank = response.json()[0].get('rank')
            count_300 = str(response.json()[0].get('statistics')['count_300'])
            count_100 = str(response.json()[0].get('statistics')['count_100'])
            count_50 = str(response.json()[0].get('statistics')['count_50'])
            output += str(pp_stat + 'pp' + '\n'
                            + map_name + ' [' + diff_name + ']' '\n'
                            + acc_stat + '%' + '\n'
                            + rank + '\n'
                            + count_300 + '/' + count_100 + '/' + count_50 + '\n')

        await ctx.send(output)

    @commands.command()
    async def user(self, ctx, username=''):
        output =''
        params= await self.get_param()
        headers= await self.get_header()
        id = await self.get_userid(username)
        response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)
        if(not response.json().get('statistics')['is_ranked']):
            output += 'This player is currently inactive'
        else:
            country_rank = str(response.json().get('statistics')['country_rank'])
            country = response.json().get('country_code')
            global_rank = str(response.json().get('statistics')['global_rank'])
            num_A = str(response.json().get('statistics')['grade_counts']['a'])
            num_S = str(response.json().get('statistics')['grade_counts']['s'])
            num_SH = str(response.json().get('statistics')['grade_counts']['sh'])
            num_SS = str(response.json().get('statistics')['grade_counts']['ss'])
            num_SSH = str(response.json().get('statistics')['grade_counts']['ssh'])
            acc = str(round(response.json().get('statistics')['hit_accuracy'], 2))
            level = str(response.json().get('statistics')['level']['current'])
            level_prog = str(response.json().get('statistics')['level']['progress'])
            playcount = str(response.json().get('statistics')['play_count'])
            time_played_hours = str(math.trunc(response.json().get('statistics')['play_time'] / 3600))
            time_played_str = str(time_played_hours + ' hours')
            pp = str(response.json().get('statistics')['pp'])
            score = str("{:,}".format(response.json().get('statistics')['ranked_score']))
            maxcombo = str(response.json().get('statistics')['maximum_combo'])
            output += str('rank : ' + global_rank + ' :globe_with_meridians: ' + country_rank + ' :flag_' + country.lower() + ': \n'
                            + 'pp : **' + pp + '** accuracy : **' + acc + '** level : ' + level + '.' + level_prog +'\n'
                            + ' playcount : ' + playcount + ' time played : ' + time_played_str + '\n'
                            + 'total score : ' + score + ' max combo : ' + maxcombo)
        
        await ctx.send(output)

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

