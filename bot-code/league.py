import discord
import datetime
import json
from discord.ext import commands, tasks 
import requests
import os

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


    @commands.Cog.listener()
    async def on_ready(self):
        if not self.rankup_loop.is_running():
            print("Starting rankup loop...")
            self.rankup_loop.start()
    
    #colors for rank based embeds
    rank_colors = {
        "" : discord.Color.from_rgb(0,0,0),
        "iron" : discord.Color.from_rgb(79, 56, 26), 
     "bronze" : discord.Color.from_rgb(156, 56, 9),
     "silver" : discord.Color.from_rgb(136, 141, 143),
     "gold" : discord.Color.from_rgb(219, 165, 18),
     "platinum" : discord.Color.from_rgb(73, 138, 154),
     "emerald" : discord.Color.from_rgb(36, 166, 27),
     "diamond" : discord.Color.from_rgb(6, 130, 201),
     "master" : discord.Color.from_rgb(222, 71, 222),
     "grandmaster" : discord.Color.from_rgb(173, 17, 54),
     "challenger" : discord.Color.from_rgb(0, 177, 252)
    }

    #NOTE: comment out whichever one you are not using 
    league_path = 'league.json' #actual bot
    #league_path = os.getcwd() + "\\bot-code\\league.json" #local
    ranks_path = "ranks.json"      #for actual bot
    #ranks_path = os.getcwd() + "\\bot-code\\ranks.json" #local testing

    #getting data from league.json
    
    def get_container(self, path):
        with open(path, "r") as file:
                container = json.load(file)
        return container
    
    #for index comparison in check_{rank/tier}_change()
    ranks = ["","iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master", "grandmaster", "challenger"]
    tiers = ["IV", "III", "II", "I"]

    def get_current_rank(self, summoner_name, ranked_type):
            rank = ""
        
            if len(summoner_name) > 0:      
                    # Spaces must be "%20" in a URL
                    user_no_space = summoner_name.replace(" ", "%20")
                    summoner = user_no_space.split("#")
                    summoner_name = summoner[0]
                    tagline = summoner[1]     
                    url = self.gameAPI_url + "/rank/" + summoner_name + "/" + tagline + "/" + ranked_type
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) > 0:
                            rank = data[0]
                            rank = rank[0] + rank[1:].lower()   # 'BRONZE' -> 'Bronze'
                            tier = data[1]
                            rank = rank + " " + tier
                            #print("this two :3" + str(rank))
                            return rank
                        else:
                            rank = ""
                            #print("this one :3")
                            return rank
            return rank
    
    #checks if a players rank went up or down, separate from tiers. Returns True if player climbed, False if player demoted
    def check_rank_change(self, initial, final):
        print("rank change")
        start = initial.split()[0].lower()
        end = final.split()[0].lower()
        print(str(self.ranks.index(start)) + " : " + str(self.ranks.index(end)))
        if(self.ranks.index(start) < self.ranks.index(end)):
            return 1
        elif(self.ranks.index(start) > self.ranks.index(end)):
            return -1
        else:
            return 0



    #checks if a player's tier went up or down. Returns True if player climbed, False if player demoted.
    def check_tier_change(self, initial, final):
        print("tier change")
        start = initial.split()[1]
        end = final.split()[1]
        print(str(self.tiers.index(start)) + " : " + str(self.tiers.index(end)))
        if(self.tiers.index(start) < self.tiers.index(end)):
            return 1
        elif(self.tiers.index(start) > self.tiers.index(end)):
            return -1
        else: 
            return 0


    tft_path = os.getcwd() + "\\bot-code\\tft.json"
    @commands.command("testembed")
    async def embedtest(self, ctx):
        test_channel = self.bot.get_channel(984494911636258847)
        container = self.get_container(self.tft_path)
        '''
        for rank in self.ranks[2:]:
            embed = discord.Embed(title=container["rank_emotes"][rank] + " Rank Update " + container["rank_emotes"][rank], description="`insert player name` has reached `insert rank`!",
                                        color=self.rank_colors[rank]).set_thumbnail(url=container["rank_icons"][rank])
        '''
        one_star = "★"
        two_star = "★★"
        three_star = "★★★"
        four_star = "★★★★"
        embed = discord.Embed(title="`{insert player name}'s` recent match", description="### Placement : `1`\n### Level : `9`\n### Stage : `6-5`", color=discord.Color.from_rgb(255, 215,0)).set_thumbnail(url="https://seeklogo.com/images/T/teamfight-tactics-logo-4B66ABB0E4-seeklogo.com.png")
        embed.add_field(name="Units", value="`Silco" + two_star + "\nMordekaiser" + two_star + "\nDr. Mundo" + two_star + "\nLeblanc" + one_star + "\nGaren" +two_star+ "\nElise"+two_star+"\nCassiopeia"+two_star+"\nVladimir"+three_star+"\nMorgana"+two_star+"`", inline=True)
        embed.add_field(name="Traits", value="`Black Rose | 5\nDominator | 4\nWatcher | 2\nSorcerer | 2\nEmissary | 1`")
        await test_channel.send(embed=embed)

    @tasks.loop(minutes=15)
    async def rankup_loop(self):
        #NOTE:COMMENT OUT WHICHEVER ONE YOU ARE NOT USING OR IT WILL GIVE ATTRIBUTE ERROR
        # this is the bot-spam channel for testing
        #channel = self.bot.get_channel(984494911636258847)
        # this is the league-track channel for actual use
        channel =self.bot.get_channel(1326681372907143228)
        with open(self.ranks_path, 'r') as file, open(self.league_path, 'r') as contain:
            data = json.load(file)
            container = json.load(contain)

        if len(data) == 0: #if no one is being tracked
            print("No one being tracked")
            return
        
        for player in data:
            current_rank = self.get_current_rank(player["summoner"], player["type"])
            if current_rank != player["rank"]:

                #if player was unranked and no longer is
                if player["rank"] == "" or player["rank"] == None:
                    rank_split = current_rank.split()[0].lower()
                    embed = discord.Embed(title=container["rank_emotes"][rank_split] + "Rank Update" + container["rank_emotes"][rank_split], description = "### `" + player["summoner"] + "` is now `" + current_rank + "`\nWas `unranked`",color=self.rank_colors[rank_split]).set_thumbnail(url=container["rank_icons"][rank_split])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue

                #if player is now unranked
                if current_rank == None or current_rank == "":
                    current_rank = ""
                    embed = discord.Embed(title=container["rank_emotes"][current_rank] + "Rank Update" + container["rank_emotes"][current_rank], description = "### `" + player["summoner"] + "` is now `unranked`\nWas `" + player["rank"] + "`",color=self.rank_colors[current_rank]).set_thumbnail(url=container["rank_icons"][current_rank])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue
                
                split_rank = current_rank.split()[0].lower()
                print(split_rank + " : "+ player["summoner"])
                #checking if the player demoted or promoted out of the rank as a whole, not just moving up or down a division

                #rank promo
                if self.check_rank_change(initial=player["rank"],final=current_rank) == 1:
                    embed = discord.Embed(title=container["rank_emotes"][split_rank] + " Promotion " + container["rank_emotes"][split_rank], 
                                          description= "### `"+player["summoner"] + "` has been promoted to `" + current_rank + "`!", color=self.rank_colors[split_rank]).set_thumbnail(url=container["rank_icons"][split_rank])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue 

                #rank demotion
                if self.check_rank_change(initial=player["rank"],final=current_rank) == -1:
                    embed = discord.Embed(title=container["rank_emotes"][split_rank] + " Demotion " + container["rank_emotes"][split_rank], 
                                          description= "### `"+player["summoner"] + "` has demoted to `" + current_rank + "`\nWas `" + player["rank"] + "`", color=self.rank_colors[split_rank]).set_thumbnail(url=container["rank_icons"][split_rank])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue
                
                #now checking if the player went up or down divisions inside of a rank

                #division promo
                if self.check_tier_change(initial=player["rank"], final=current_rank) == 1:
                    embed = discord.Embed(title=container["rank_emotes"][split_rank] + " Rank Update " + container["rank_emotes"][split_rank], 
                                          description= "### `"+player["summoner"] + "` has reached `" + current_rank + "`!",color=self.rank_colors[split_rank]).set_thumbnail(url=container["rank_icons"][split_rank])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue

                #division demotion
                
                if self.check_tier_change(initial=player["rank"], final=current_rank) == -1:
                    embed = discord.Embed(title=container["rank_emotes"][split_rank] + " Rank Update " + container["rank_emotes"][split_rank], 
                                          description= "### `"+player["summoner"] + "` has fallen to `" + current_rank + "`",color=self.rank_colors[split_rank]).set_thumbnail(url=container["rank_icons"][split_rank])
                    player["rank"] = current_rank
                    await channel.send(embed=embed)
                    continue
                    
        
        with open(self.ranks_path, "w") as outfile:
            json.dump(data, outfile, indent=4)
            outfile.flush()

    @rankup_loop.before_loop
    async def before_rankup_loop(self):
        await self.bot.wait_until_ready()
    
    def sort_by_mastery(self, x):
        return x[1][1]
       
    @commands.command("loltracklist")
    async def tracklist(self, ctx):
        container = self.get_container(self.league_path)
        with open(self.ranks_path, "r") as file:
            tracked = json.load(file)
        if len(tracked) == 0:
            await ctx.send("No users tracked")
        output = ""
        for player in tracked:
            if player["rank"] == "":
                output += "`" + player["summoner"] + "` | `unranked` | `" + player["queue"] + "`\n"
            else:
                output += "`" + player["summoner"] + "` | `"+ player["rank"] + "` | `" + player["queue"] + "`\n"
        
        embed = discord.Embed(title="Tracked Users", description=output, color=discord.Color.from_rgb(9, 102, 217)).set_thumbnail(url=container["logo"])
        await ctx.send(embed=embed)
    
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
                        
                        dict = {"summoner" : summoner_fullname, "rank" : full_rank, "type" : ranked_type, "queue" : ranked_queue}
                        
                        #checking if user is already added
                        with open(self.ranks_path, "r") as file:
                            data = json.load(file)
                        for dictionary in data:
                            if "summoner" in dictionary and dictionary["summoner"] == summoner_fullname:
                                await ctx.send("`" + summoner_fullname + "` is already being tracked")
                                return
                        #adding user to rank tracking json
                        data.append(dict)
                        with open(self.ranks_path, "w") as outfile:
                                json.dump(data, outfile, indent=4)
                        await ctx.send("`" + summoner_fullname + "`" + " `" + ranked_type + "` has been added to rank tracking!")
                        
                    else:
                        full_rank = ""
                        ranked_queue = self.ranked_types[ranked_type]
                        summoner_fullname = summoner_name + "#" + str(tagline)
                        dict = {"summoner" : summoner_fullname, "rank" : full_rank, "type" : ranked_type, "queue" : ranked_queue}
                        
                        #checking if user is already added
                        with open(self.ranks_path, "r") as file:
                            data = json.load(file)
                        for dictionary in data:
                            if "summoner" in dictionary and dictionary["summoner"] == summoner_fullname:
                                await ctx.send("`" + summoner_fullname + "` is already being tracked")
                                return
                        #adding user to rank tracking json
                        data.append(dict)
                        with open(self.ranks_path, "w") as outfile:
                                json.dump(data, outfile, indent=4)
                                outfile.flush()
                        await ctx.send("`" + summoner_fullname + "`" + " `" + ranked_type + "` has been added to rank tracking!")
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
                #if user enters an invalid type
                try:
                    int(input[1])
                except ValueError:
                    await ctx.send("This command only accepts integers as a parameter, try adding a number after the $ instead. EX : `m!lolmastery ShadowShark19#190 $5`")
                    return
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
            container = self.get_container(self.league_path)
            if "$" in summoner_name:
                # Spaces must be "%20" in a URL
                input = summoner_name.split("$")
                user_strip = input[0].strip()
                user_no_space = user_strip.replace(" ", "%20")
                summoner = user_no_space.split("#")
                summoner_name = summoner[0]
                tagline = summoner[1]     
                 #if user enters an invalid type
                try:
                    int(input[1])
                    valid_int = True
                except ValueError:
                    valid_int = False
                if not valid_int:
                    ranked_type = input[1].upper()  # Clean up the input, make it all uppercase
                    url = self.gameAPI_url + "/rank/" + summoner_name + "/" + tagline + "/" + ranked_type
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) > 0:
                            name = input[0]
                            rank = data[0]
                            rank = rank[0] + rank[1:].lower()   # 'BRONZE' -> 'Bronze'
                            tier = data[1]
                            embed = discord.Embed(title=":trophy: Summoner Rank :trophy:", description=name,
                                                color=self.rank_colors[rank.lower()]).set_thumbnail(url=container["rank_icons"][rank.lower()])
                            lp = str(data[2])
                            ranked_queue = self.ranked_types[ranked_type]
                            embed.add_field(name=ranked_queue, value=rank+" "+tier+", "+lp+" LP", inline=False)
                            await ctx.send(embed=embed)
                            
                        else:
                            await ctx.send("No ranked data found for that summoner with that ranked type :man_shrugging:")
                    else:
                        await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
                else:
                    await ctx.send("This command does not accept integers as a parameter, try adding text after the $ instead. EX : `m!lolrank ShadowShark19#190 $SOLO`")
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

                #if user enters an invalid type
                try:
                    int(input[1])
                except ValueError:
                    await ctx.send("This command only accepts integers as a parameter, try adding a number after the $ instead. EX : `m!lolmatches ShadowShark19#190 $5`")
                    return
                
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

                 #if user enters an invalid type
                
                try:
                    int(input[1])
                except ValueError:
                    await ctx.send("This command only accepts integers as a parameter, try adding a number after the $ instead. EX : `m!lolmatch ShadowShark19#190 $1`")
                    return
                
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
        