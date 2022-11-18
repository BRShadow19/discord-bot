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
    
    async def get_header(self):
        """Retrieves the header dictionary
            Returns:
                headers: the header dictionary
        """
        token = await self.get_token()
        headers = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }

        return headers
    
    async def get_param(self):
        """Retrieves the params dictionary
            Returns:
                params: the params dictionary
        """
        params = {
            'mode' : 'osu',
            'limit' : 5
        }
        return params


    async def change_param(self, mode, limit):
        """Can be used to change the values of the params dictionary, which includes the osu! mode and the limit on number of results displayed
            by the API.
            Args:
                mode(str): the osu! mode (currently only supports osu!std)
                limit(int): the number of results displayed by the API
            Returns:
                params: the new params dictionary
        """
        params = {
            'mode' : mode,
            'limit' : limit
        }
        return params
    
    
    async def get_userid(self, username):
        """Retrieves the user's osu! account ID from their osu! username
            Args:
                username(str): the user's osu! username
            Returns:
                returns the user's osu! ID
        """
        params= await self.get_param()
        headers= await self.get_header()
        data = requests.get(f'{API_URL}/users/{username}', params = params,  headers = headers)
        return str(data.json().get('id'))

    async def check_link(self, user):
        """Checks if the discord user that input the command has their osu account linked to the bot
            Args:
                user(str): the user's discord username and code ex: Username#1234
            Returns:
                returns true if the user is in the linked_users dictionary
        """
        linked_users = {
            'AmphibiousBean#8924' : await self.get_userid('amphibiousbean'),
            'ShadowShark19#1345' : await self.get_userid('shadowshark19'),
            'Toradorable#8947' : await self.get_userid('slayera321')
        }
        return user in linked_users.keys()

    
    @commands.command()
    async def top(self, ctx, username=''): 
        """Sends an embedded message that contains a user's top 5 performance plays in osu! standard along with the information for each play:
            - Beatmap name with difficulty name
            - performance points
            - accuracy
            - rank (SSH, SS, SH, S, A, B, C, D)
            - number of 300s, 100s, 50s, and misses in a format of 300/100/50/miss
        Args:
            ctx (obj): Object containing all information about the context of the bot within a Discord server,
                such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            username(str, optional): The username of the user who's plays are to be displayed. Defaults to ''. 
        Returns: 
            None: If the user does not give a username and is not already linked with the bot, the function will return None. 
        """
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
        """Sends an embedded message that contains the users most recent submitted play, pass or fail, along with information regarding the play:
            - Username
            - Beatmap name with difficulty name
            - Mods
            - Performance points
            - Accuracy
            - Rank
            - Number of 300s, 100s, 50s, and misses in the format of 300/100/50/miss
            Args:
                ctx (obj): Object containing all information about the context of the bot within a Discord server,
                    such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
                username(str, optional): The username of the user who's recent play is to be displayed. Defaults to ''. 
            Returns:
                None: If the user does not give a username and is not already linked with the bot, the function will return None.
        """
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
            self.beatmap_id = str(response.json()[0].get('beatmap')['id'])
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
            self.beatmap_id = str(response.json()[0].get('beatmap')['id'])
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
        """Sends an embedded message that contains the profile information and statistics of a given user:
            - Username
            - Total ranked score
            - Rank (global and country)
            - Profile accuracy
            - Account level
            - Total playcount
            - Time played (in hours)
            - Total performance points
            - Maximum combo acheived
            - Number of SSH, SH, SS, S, and A ranks
            Args:
                ctx (obj): Object containing all information about the context of the bot within a Discord server,
                    such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
                username(str, optional): The username of the user who's recent play is to be displayed. Defaults to ''. 
            
        """
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
        """Sends an embedded message that contains information about a given beatmap through either a link that is passed as a parameter or
            through the self.beatmap_id variable, which takes the beatmap from the most recent use of m!rs as the beatmap.
            The information displayed will be:
                - Beatmap name with difficulty name
                - Difficulty stats (OD, AR, CS)
                - Circle/Slider/Spinner count
                - Star rating
                - BPM
                - Mapper name
                - Ranked status
                - Playcount
                - Length
                - Max combo
            Args:
                ctx(obj): Object containing all information about the context of the bot within a Discord server,
                    such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
                link(str): the beatmap link for the beatmap to be shown. Defaults to ''
        """
        params= await self.get_param()
        headers= await self.get_header()
        output = ''
        if(not len(link) == 0):
            output += 'link'
        elif (not len(self.beatmap_id) == 0 and len(link) == 0):
            response = requests.get(f'{API_URL}/beatmaps/' + self.beatmap_id    , params=params, headers=headers)
            #output += 'self.beatmap no link'    
        else: 
            output += 'no beatmap linked'
        
        od = str(response.json().get('accuracy'))
        ar = str(response.json().get('ar'))
        cs = str(response.json().get('cs'))
        bpm = str(response.json().get('beatmapset')['bpm'])
        title = response.json().get('beatmapset')['title']
        artist = response.json().get('beatmapset')['artist']
        ranked_status = response.json().get('status')
        max_combo = str(response.json().get('max_combo'))
        star_rating = str(response.json().get('difficulty_rating'))
        circle_count = str(response.json().get('count_circles'))
        slider_count = str(response.json().get('count_sliders'))
        spinner_count = str(response.json().get('count_spinners'))
        playcount = str(response.json().get('playcount'))
        lengthRemainder = str(response.json().get('total_length') % 60)
        lengthMinutes = str(response.json().get('total_length') // 60)
        length = str(lengthMinutes + ':' + lengthRemainder)
        backgroundURL = response.json().get('beatmapset')['covers']['card']
        output += str(od + ' ' + ar + ' ' + cs + ' ' + bpm + ' ' + title + ' ' + artist + ' ' + ranked_status + ' ' + max_combo + ' ' 
                        + star_rating + ' ' + circle_count + '/' + slider_count + '/' + spinner_count + ' ' + playcount + ' ' + length)
                        
        g = discord.Embed(description=output,color=discord.Color.from_rgb(255, 152, 197)).set_thumbnail(url=backgroundURL)
                                
        await ctx.send(embed=g)




        
        


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

