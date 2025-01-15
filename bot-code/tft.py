import discord
import datetime
import json
from discord.ext import commands, tasks 
import requests
import os

class tft(commands.Cog):

    def __init__(self, bot, gameAPI_url):
        self.bot = bot
        self.gameAPI_url = gameAPI_url+"/tft"
        self.ranked_types = {   "SOLO": "Ranked TFT",
                                "DOUBLEUP": "Double Up"
                            }
    

    '''
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.rankup_loop.is_running():
            print("Starting rankup loop...")
            self.rankup_loop.start()
    '''
    #league_path = 'league.json' #actual bot
    league_path = os.getcwd() + "\\bot-code\\league.json" #local

    def get_container(self, path):
        with open(path, "r") as file:
                container = json.load(file)
        return container

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

    @commands.command("tftrank")
    async def rank(self, ctx, *, summoner_name=""):
        """Call GameAPI (https://github.com/BRShadow19/GameAPI) to gather the TFT ranked level
            for a given summoner name and ranked queue type. User input would look like m!tftrank ShadowShark19#190 $solo

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                        such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            summoner_name (str, optional): Name of the summoner to get rank of, as well as the ranked queue type after a '$'. Defaults to "".
        """
        container = self.get_container(self.league_path)
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
                await ctx.send("Try again, make sure to enter a ranked type.  Ex: ShadowShark19#190 $SOLO")
        else: 
            await ctx.send("To use this command, enter a summoner name and the ranked type, with a '$' before the rank. Options are SOLO or DOUBLEUP. Ex: ShadowShark19#190 $SOLO")
    


    @commands.command("tftmatch")
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
                #TODO: change this for tft xdd (its still just ctrl c ctrl v from league.py)
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
        await bot.add_cog(tft(bot, gameAPI_url=url))
        print("TFT is online!")