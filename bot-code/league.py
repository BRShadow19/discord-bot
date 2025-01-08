import discord
import datetime
import json
from discord.ext import commands, tasks 
import requests

class league(commands.Cog):
    """This class contains all League of Legends commands for the bot
    """

    def __init__(self, bot, gameAPI_url):
        self.bot = bot
        self.gameAPI_url = gameAPI_url+"/league"
        self.ranked_types = {   "SOLO": "Solo/Duo",
                                "FLEX": "Flex 5v5",
                                "TFT": "TFT"
                            }
    #emotes in testing server
    rank_emotes = {
    "iron" : "<:iron:1326622103478210680>", 
     "bronze" : "<:bronze:1326622098533257298>",
     "silver" : "<:silver:1326622102207467540>",
     "gold" : "<:gold:1326622097279160330>",
     "platinum" : "<:platinum:1326622099887882331>",
     "emerald" : "<:emerald:1326622929936453672>",
     "diamond" : "<:diamond:1326622096222322688>",
     "master" : "<:master:1326622104522592389>",
     "grandmaster" : "<:grandmaster:1326622106959740928>",
     "challenger" : "<:challenger:1326622105785073704>"
    }
    #colors for rank based embeds
    rank_colors = {
        "iron" : discord.Color.from_rgb(79, 56, 26), 
     "bronze" : discord.Color.from_rgb(156, 56, 9),
     "silver" : discord.Color.from_rgb(136, 141, 143),
     "gold" : discord.Color.from_rgb(219, 165, 18),
     "platinum" : discord.Color.from_rgb(39, 230, 172),
     "emerald" : discord.Color.from_rgb(36, 166, 27),
     "diamond" : discord.Color.from_rgb(6, 130, 201),
     "master" : discord.Color.from_rgb(222, 71, 222),
     "grandmastser" : discord.Color.from_rgb(173, 17, 54),
     "challenger" : discord.Color.from_rgb(0, 177, 252)
    }

    ranks = ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master", "grandmaster", "challenger"]
    tiers = ["IV", "III", "II", "I"]

    utc = datetime.timezone.utc
    #loops at 0:00, 6:00, 12:00, 18:00 EST (5:00, 11:00, 17:00, 23:00 UTC)
    times = [datetime.time(hour=5,tzinfo=utc), datetime.time(hour=11, tzinfo=utc), 
             datetime.time(hour=17,tzinfo=utc), datetime.time(hour=23, tzinfo=utc)]
    
    def get_current_rank(self, summoner_name):
        rank = ""
        try:
            if len(summoner_name) > 0:
                if "$" in summoner_name:
                    # Spaces must be "%20" in a URL
                    input = summoner_name.split("$")
                    user_strip = input[0].strip()
                    user_no_space = user_strip.replace(" ", "%20")
                    summoner = user_no_space.split("#")
                    summoner_name = summoner[0]
                    tagline = summoner[1]     
                    ranked_type = input[1].upper()  # Clean up the input, make it all uppercase
                    url = self.gameAPI_url + "/rank/" + summoner_name + "/" + tagline + "/" + ranked_type
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) > 0:
                            rank = data[0]
                            rank = rank[0] + rank[1:].lower()   # 'BRONZE' -> 'Bronze'
                            tier = data[1]
                            rank = rank + " " + tier
                            return rank
        except:
            print("broke :(")
            return rank
    
    #checks if a players rank went up or down, separate from tiers. Returns True if player climbed, False if player demoted
    def check_rank_change(self, initial, final):
        start = initial.split()[0].lower()
        end = final.split()[0].lower()
        if(self.ranks.index(start) < self.ranks.index(final)):
            return True
        else:
            return False



    #checks if a player's tier went up or down. Returns True if player climbed, False if player demoted.
    def check_tier_change(self, initial, final):
        start = initial.split()[1]
        end = final.split()[1]
        if(self.tiers.index(start) < self.tiers.index(final)):
            return True
        else:
            return False
        

    @commands.command("testembed")
    async def embedtest(self, ctx):
        for rank in self.ranks:
            embed = discord.Embed(title=self.rank_emotes[rank] + " Rank Update " + self.rank_emotes[rank], description="`insert player name` has reached `insert rank`!",
                                        color=self.rank_colors[rank])
            await ctx.send(embed=embed)



    '''
    @tasks.loop(time=times)
    async def check_rankup_loop(self, ctx):

        with open("ranks.json", "r") as file:
            data = json.load(file)
        for player in data:
            current_rank = self.get_current_rank(player["summoner"])
            if current_rank != player["rank"]:
                if self.check_rank_change(initial=player["rank"],final=current_rank):
                    embed = discord.Embed(title=self.rank_emotes[current_rank.split()[0].lower()] + " Promotion " + self.rank_emotes[current_rank.split()[0].lower()], 
                                          description= "`"+player["summoner"] + "` has been promoted to `" + current_rank + "`!")
                elif(self.check_rank_change(initial=player["rank"],final=current_rank) is False):
                    embed = discord.Embed(title=self.rank_emotes[current_rank.split()[0].lower()] + " Demotion " + self.rank_emotes[current_rank.split()[0].lower()], 
                                          description= "`"+player["summoner"] + "` has demoted to `" + current_rank + "`!")
    '''

    
    def sort_by_mastery(self, x):
        return x[1][1]
       
    
    
    @commands.command("loltrackadd")
    async def trackadd(self, ctx, *, summoner_name = ""):
        if len(summoner_name) > 0:
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                ranked_type = input[1].upper()  # Clean up the input, make it all uppercase
                url = self.gameAPI_url + "/rank/" + summoner_name + "/" + tagline + "/" + ranked_type
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        rank = data[0]
                        rank = rank[0] + rank[1:].lower()   # 'BRONZE' -> 'Bronze'
                        tier = data[1]
                        ranked_queue = self.ranked_types[ranked_type]
                        full_rank = rank + " " + tier
                        summoner_fullname = summoner_name + "#" + str(tagline)
                        
                        dict = {"summoner" : summoner_fullname, "rank" : full_rank, "queue" : ranked_queue}
                        
                        #checking if user is already added
                        with open("ranks.json", "r") as file:
                            data = json.load(file)
                        for dictionary in data:
                            if "summoner" in dictionary and dictionary["summoner"] == summoner_fullname:
                                await ctx.send("`" + summoner_fullname + "` is already being tracked")
                                return
                        #adding user to rank tracking json
                        data.append(dict)
                        with open("ranks.json", "w") as outfile:
                                json.dump(data, outfile, indent=4)
                        await ctx.send("`" + summoner_fullname + "`" + " `" + ranked_type + "` has been added to rank tracking!")
                        
                    else:
                        await ctx.send("No ranked data found for that summoner with that ranked type :man_shrugging:")
                else:
                    await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
            else:
                await ctx.send("Try again, make sure to enter a ranked type.  Ex: ShadowShark19 $SOLO")
        else: 
            await ctx.send("To use this command, enter a summoner name and the ranked type, with a '$' before the rank. Options are SOLO, FLEX, or TFT. Ex: ShadowShark19 $SOLO")
    

    @commands.command("lolmastery")
    async def mastery(self, ctx, *, summoner_name=""):
        """Call GameAPI (https://github.com/BRShadow19/GameAPI) to gather League of Legends champion mastery statistics
            for a given summoner name. User input would look like m!lolmastery ShadowShark19 $5

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                        such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            summoner_name (str, optional): Name of the summoner to get mastery stats on, and the number of champions
                                            after a '$'. Defaults to "".
        """
        if len(summoner_name) > 0:
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                count = input[1]
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                url = self.gameAPI_url + "/mastery/" + summoner_name + "/" + tagline + "/" + count
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    name = input[0]
                    embed = discord.Embed(title=":fire: Highest Champion Mastery :fire:", description=name,
                                        color=discord.Color.gold())
                    # Sort the dictionary of champions based on number of mastery points
                    data = dict(sorted(data.items(), key=self.sort_by_mastery, reverse=True))
                    for champion in data:   # Create a new embed field for each champion
                        level = str(data[champion][0])
                        points = str(data[champion][1])
                        embed.add_field(name=champion, value="M"+level+"     "+points+" pts", inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
            else:
                await ctx.send("Try again, make sure to enter a number of champions.  Ex: ShadowShark19 $5")
        else: 
            await ctx.send("To use this command, enter a summoner name and the number of champions, with a '$' before the number.  Ex: ShadowShark19 $5")


    @commands.command("lolrank")
    async def rank(self, ctx, *, summoner_name=""):
        """Call GameAPI (https://github.com/BRShadow19/GameAPI) to gather the League of Legends ranked level
            for a given summoner name and ranked queue type. User input would look like m!lolmastery ShadowShark19 $solo

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                        such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            summoner_name (str, optional): Name of the summoner to get mastery stats on, and the number of champions
                                            after a '$'. Defaults to "".
        """
        if len(summoner_name) > 0:
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                ranked_type = input[1].upper()  # Clean up the input, make it all uppercase
                url = self.gameAPI_url + "/rank/" + summoner_name + "/" + tagline + "/" + ranked_type
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        name = input[0]
                        embed = discord.Embed(title=":trophy: Summoner Rank :trophy:", description=name,
                                            color=discord.Color.gold())
                        rank = data[0]
                        rank = rank[0] + rank[1:].lower()   # 'BRONZE' -> 'Bronze'
                        tier = data[1]
                        lp = str(data[2])
                        ranked_queue = self.ranked_types[ranked_type]
                        embed.add_field(name=ranked_queue, value=rank+" "+tier+", "+lp+" LP", inline=False)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("No ranked data found for that summoner with that ranked type :man_shrugging:")
                else:
                    await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
            else:
                await ctx.send("Try again, make sure to enter a ranked type.  Ex: ShadowShark19 $SOLO")
        else: 
            await ctx.send("To use this command, enter a summoner name and the ranked type, with a '$' before the rank. Options are SOLO, FLEX, or TFT. Ex: ShadowShark19 $SOLO")


    @commands.command("lolmatches")
    async def match_history(self, ctx, *, summoner_name=""):
        """Call GameAPI (https://github.com/BRShadow19/GameAPI) to gather League of Legends match history
            for a given summoner name, with a given number of matches. User input for the 5 most recent matches 
            would look like m!lolmatches ShadowShark19 $5

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                        such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            summoner_name (str, optional): Name of the summoner to get the match history of, and the number of matches
                                            after a '$'. Defaults to "".
        """
        if len(summoner_name) > 0:
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                count = input[1]
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                url = self.gameAPI_url + "/matches/" + summoner_name + "/" + tagline + "/" +count
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        name = input[0]
                        embed = discord.Embed(title=":crossed_swords: "+count+" Most Recent Matches :crossed_swords:", description=name,
                                            color=discord.Color.gold())
                        for i in range(len(data)):   # Create a new embed field for each match
                            match_number = str(i+1)
                            match = data[i] # dict of the match stats
                            did_win = match["win"]
                            kda = match["KDA"]
                            champion = match["championName"]
                            multikill = match["largestMultikill"]
                            queue_type = match["queueType"]
                            largest_kill = ""
                            if multikill >= 3:
                                largest_kill = "\n"+match["multikillType"]
                            if did_win:
                                embed.add_field(name=":green_circle: Match "+match_number+": Victory!", value=queue_type+"\nChampion: "+champion+"\nK/D/A: "+kda+largest_kill, inline=False)
                            else: 
                                embed.add_field(name=":red_circle: Match "+match_number+": Defeat!", value=queue_type+"\nChampion: "+champion+"\nK/D/A: "+kda+largest_kill, inline=False)
                            embed.set_footer(text="For detailed info on a match -> m!lolmatch")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("No recent matches found for that summoner :man_shrugging:")
                else:
                    await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
            else:
                await ctx.send("Try again, make sure to enter a number of matches.  Ex: ShadowShark19 $5")
        else: 
            await ctx.send("To use this command, enter a summoner name and the number of matches to obtain, with a '$' before the number.  Ex: ShadowShark19 $5")
            
            
    @commands.command("lolmatch")
    async def match_details(self, ctx, *, summoner_name=""):
        """Call GameAPI (https://github.com/BRShadow19/GameAPI) to gather League of Legends match stats
            for a given summoner name, with a match number. User input for the second-most recent match 
            would look like m!lolmatch ShadowShark19 $2

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                        such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            summoner_name (str, optional): Name of the summoner to get the detailed match stats of, and the match
                                            after a '$'. Defaults to "".
        """      
        if len(summoner_name) > 0:
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                start = input[1]
                url = self.gameAPI_url + "/match/" + summoner_name +"/" + tagline + "/" +start
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        match = data[0]
                        name = input[0]
                        did_win = match["win"]
                        queue_type = match["queueType"]
                        if did_win:
                            embed = discord.Embed(title=":crossed_swords: Detailed Stats for Match "+start+" (Victory) :crossed_swords:", description=name+"\n"+queue_type,
                                                color=discord.Color.gold())
                        else:
                            embed = discord.Embed(title=":crossed_swords: Detailed Stats for Match "+start+" (Defeat) :crossed_swords:", description=name+"\n"+queue_type,
                                                color=discord.Color.gold())
                        kda = match["KDA"]
                        champion = match["championName"]
                        cs = match["CS"]
                        cs_per_min = match["CS/min"]
                        champion_damage = match["championDamage"]
                        damage_per_minute = match["damage/min"]
                        duration = match["duration"]
                        gold = match["goldEarned"]
                        gold_per_minute = match["gold/min"]
                        self_mit_damage = match["selfMitigatedDamage"]
                        vision_score = match["visionScore"]
                        multikill = match["largestMultikill"]
                        largest_kill = ""
                        if multikill >= 3:
                            largest_kill = "\n"+match["multikillType"]
                        embed.add_field(name="Match Duration", value=duration, inline=False)
                        embed.add_field(name="Champion", value=champion, inline=False)
                        embed.add_field(name="K/D/A", value=kda+largest_kill, inline=False)
                        embed.add_field(name="CS", value="Total CS: "+cs+"\nCS/min: "+cs_per_min, inline=False)
                        embed.add_field(name="Damage to Champions", value="Total Damage: "+champion_damage+"\nDamage/min: "+damage_per_minute, inline=False)
                        embed.add_field(name="Gold Earned", value="Total Gold: "+gold+"\nGold/min: "+gold_per_minute, inline=False)
                        embed.add_field(name="Self-Mitigated Damage", value=self_mit_damage, inline=False)
                        embed.add_field(name="Vision Score", value=vision_score, inline=False)
                        embed.set_footer(text="To view multiple matches -> m!lolmatches")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("No recent matches found for that summoner :man_shrugging:")
                else:
                    await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
            else:
                await ctx.send("Try again, make sure to enter the number of the match you want.  Ex: ShadowShark19 $1")
        else: 
            await ctx.send("To use this command, enter a summoner name and the match number to obtain, with a '$' before the number.  Ex: ShadowShark19 $1")


async def setup(bot, url):
    """Adds this cog to the bot, meaning that the commands in the League class can be used by the bot/users

        Args:
            bot (discord.Bot): The bot object to have the cog added to
    """    
    await bot.add_cog(league(bot, gameAPI_url=url))
    print("League is online!")
        