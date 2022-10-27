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
        self.beatmap_id = ''
        
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

    #checks if discord user has their osu user linked
    async def check_link(self, user):
        linked_users = {
            'AmphibiousBean#8924' : await self.get_userid('amphibiousbean'),
            'ShadowShark19#1345' : await self.get_userid('shadowshark19'),
            'Toradorable#8947' : await self.get_userid('slayera321')
        }
        return user in linked_users.keys()

    #gives a list of the users top 5 pp plays 
    @commands.command()
    async def top(self, ctx, username=''): 
        linked_users = {
            'AmphibiousBean#8924' : await self.get_userid('amphibiousbean'),
            'ShadowShark19#1345' : await self.get_userid('shadowshark19'),
            'Toradorable#8947' : await self.get_userid('slayera321')
        }
        user = str(ctx.author)
        params= await self.get_param()
        headers= await self.get_header()
        performance_stat = ''
        n = params.get('limit')
        if not await self.check_link(user) or not len(username) == 0:
            id = await self.get_userid(username)
            response = requests.get(f'{API_URL}/users/{id}/scores/best', params=params, headers=headers)
        elif not await self.check_link(user) and len(username) == 0:
            performance_stat += 'no user found, pass a username parameter or link your osu account'
            await ctx.send(performance_stat)
            return None
        else:
            id = linked_users.get(user)
            response = requests.get(f'{API_URL}/users/{id}/scores/best', params=params, headers=headers)
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
        linked_users = {
            'AmphibiousBean#8924' : await self.get_userid('amphibiousbean'),
            'ShadowShark19#1345' : await self.get_userid('shadowshark19'),
            'Toradorable#8947' : await self.get_userid('slayera321')
        }
        user = str(ctx.author)
        params= await self.get_param()
        headers= await self.get_header()
        output= ''
        if user not in linked_users.keys() or not len(username) == 0:
            id = await self.get_userid(username)
            username_response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)
            username = username_response.json().get('username')
            response = requests.get(f'{API_URL}/users/{id}/scores/recent?include_fails=1', params=params, headers=headers)
            beatmap = requests.get(f'{API_URL}/beatmaps/' + str(response.json()[0].get('beatmap')['id']), params=params, headers=headers)
            self.beatmap = str(response.json()[0].get('beatmap')['id'])
        elif user not in linked_users.keys() and len(username) == 0:
            output += 'no user found, pass a username parameter or link your osu account'
            await ctx.send(output)
            return None

        else:
            id = linked_users.get(user)
            response = requests.get(f'{API_URL}/users/{id}/scores/recent?include_fails=1', params=params, headers=headers)
            username_response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)
            username = username_response.json().get('username')
            beatmap = requests.get(f'{API_URL}/beatmaps/' + str(response.json()[0].get('beatmap')['id']), params=params, headers=headers)
            self.beatmap = str(response.json()[0].get('beatmap')['id'])
        #avatar = str(response.json().get('avatar_url'))
        beatmap_cover = beatmap.json().get('beatmapset')['covers']['list']
        map_name = response.json()[0].get('beatmapset')['title']
        diff_name = response.json()[0].get('beatmap')['version']
        acc_stat = str(round(response.json()[0].get('accuracy') * 100, 2))
        rank = response.json()[0].get('rank')
        count_300 = str(response.json()[0].get('statistics')['count_300'])
        count_100 = str(response.json()[0].get('statistics')['count_100'])
        count_50 = str(response.json()[0].get('statistics')['count_50'])
        miss_count = str(response.json()[0].get('statistics')['count_miss'])
        mods = str(response.json()[0].get('mods'))
        
        if(len(response.json()) == 0):

            output += 'No recent plays from `' + username + '`'

            g = discord.Embed(title="{}'s recent play".format(username), 
                            description=output,color=discord.Color.from_rgb(255, 152, 197))

        elif(not response.json()[0].get('passed')):

            output += str('**0pp** - ' + map_name + ' [' + diff_name + '] + ' + mods[2:-2] + '\n'
                            + rank + ' - ' + acc_stat + '%  ' + count_300 + '/' + count_100 + '/' + count_50 + '/' + miss_count + '\n')

            g = discord.Embed(title="{}'s recent play".format(username), 
                            description=output,color=discord.Color.from_rgb(255, 152, 197)).set_thumbnail(url=beatmap_cover)
        else:
            pp_stat = str(round(response.json()[0].get('pp'), 2))
            output += str('**' + pp_stat + 'pp** - ' + map_name + ' [' + diff_name + ']' '\n'
                            + rank + ' - ' + acc_stat + '%' + '\n'
                            + count_300 + '/' + count_100 + '/' + count_50 + '/' + miss_count + '\n')

            g = discord.Embed(title="{}'s recent play".format(username), 
                            description=output,color=discord.Color.from_rgb(255, 152, 197)).set_thumbnail(url=beatmap_cover)
                                
        await ctx.send(embed=g)

    @commands.command()
    async def user(self, ctx, username=''):
        output =''
        params= await self.get_param()
        headers= await self.get_header()
        id = await self.get_userid(username)
        response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)
        if(not response.json().get('statistics')['is_ranked']):
            output += 'This player is currently inactive'
            g = discord.Embed(title="{}\'s profile".format(username),
                                description=output,color=discord.Color.from_rgb(255, 152, 197))
        else:
            score = str("{:,}".format(response.json().get('statistics')['ranked_score']))
            country_rank = str("{:,}".format(response.json().get('statistics')['country_rank']))
            country = response.json().get('country_code')
            global_rank = str("{:,}".format(response.json().get('statistics')['global_rank']))
            num_A = str(response.json().get('statistics')['grade_counts']['a'])
            num_S = str(response.json().get('statistics')['grade_counts']['s'])
            num_SH = str(response.json().get('statistics')['grade_counts']['sh'])
            num_SS = str(response.json().get('statistics')['grade_counts']['ss'])
            num_SSH = str(response.json().get('statistics')['grade_counts']['ssh'])
            acc = str(round(response.json().get('statistics')['hit_accuracy'], 2))
            level = str(response.json().get('statistics')['level']['current'])
            level_prog = str(response.json().get('statistics')['level']['progress'])
            playcount = str("{:,}".format(response.json().get('statistics')['play_count']))
            time_played_hours = str(math.trunc(response.json().get('statistics')['play_time'] / 3600))
            time_played_str = str(time_played_hours + ' hours')
            pp = str(response.json().get('statistics')['pp'])
            score = str("{:,}".format(response.json().get('statistics')['ranked_score']))
            maxcombo = str(response.json().get('statistics')['maximum_combo'])
            avatar = str(response.json().get('avatar_url'))
            output += str('rank : ' + global_rank + ' :globe_with_meridians: ' + country_rank + ' :flag_' + country.lower() + ': \n'
                            + 'pp : **' + pp + '** accuracy : **' + acc + '%** level : ' + level + '.' + level_prog +'\n'
                            + ' playcount : ' + playcount + ' time played : ' + time_played_str + '\n'
                            + 'total score : ' + score + ' max combo : ' + maxcombo)
            g = discord.Embed(title="{}\'s profile".format(username),
                                description=output,color=discord.Color.from_rgb(255, 152, 197)).set_thumbnail(url=avatar)
        await ctx.send(embed=g)

    @commands.command()
    async def beatmap(self, ctx, link=''):
        params= await self.get_param()
        headers= await self.get_header()
        output = ''
        if(not len(link) == 0):
            output += 'link'
        elif (not len(self.beatmap_id) == 0 and len(link) == 0):
            response = requests.get(f'{API_URL}/beatmaps/' + self.beatmap, params=params, headers=headers)
            output += 'self.beatmap no link'    
        else: 
            output += 'no beatmap linked'
        
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

