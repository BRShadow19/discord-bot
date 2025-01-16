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
    #tft_path = 'tft.json' #actual bot
    tft_path = os.getcwd() + "\\bot-code\\tft.json" #local

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

    result_colors = {
        "1" : discord.Color.from_rgb(219, 165, 18),
        "2" : discord.Color.from_rgb(136, 141, 143),
        "3" : discord.Color.from_rgb(156, 56, 9),
        "4" : discord.Color.from_rgb(64, 49, 42)

    }

    star_levels_str= { #this apparently breaks when in tft.json and outputs "˜…â˜…", so its gotta be here i suppose..
            "1" : "★",
            "2" : "★★",
            "3" : "★★★",
            "4" : "★★★★"
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
        container = self.get_container(self.tft_path)
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
                    await ctx.send("This command only accepts integers as a parameter, try adding a number after the $ instead. EX : `m!tftmatch ShadowShark19#190 $1`")
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
                        placement = match["placement"]
                        level = match["level"]
                        round_reached = match["round"]
                        time = match["time_elim"]
                        traits = match["traits"]
                        units = match["units"]

                        if did_win == True:
                            color = self.result_colors[placement]
                        else:
                            color = discord.Color.from_rgb(48, 48, 48)
                        traits_out = ""
                        units_out ="`"
                        for trait in traits:
                            if trait["style"] > 0:
                                trait_name = container["traits_code_to_real"][trait["name"]]
                                traits_out += container["trait_icons_emote"][trait_name] + "`" + trait_name + " | " + str(trait["num_units"]) + "` " + container["trait_tier_emotes"][str(trait["style"])] + "\n"
                        traits_out += "`"
                        print(traits)
                        for unit in units:
                            units_out += container["units_code_to_real"][unit["name"]] + self.star_levels_str[unit["star"]] + "\n"
                        units_out += "`"
                        
                        embed = discord.Embed(title="`" + name + "'s` recent TFT match", 
                                              description="### Placement : `" + placement + "`\n### Level : `" + level + "`\n### Round : `" + round_reached + "`",
                                              color=color).set_thumbnail(url="https://seeklogo.com/images/T/teamfight-tactics-logo-4B66ABB0E4-seeklogo.com.png")
                        embed.add_field(name="Units", value=units_out, inline=True)
                        embed.add_field(name="Traits", value=traits_out, inline=True)
                        embed.set_footer(text="Match length : " + time)
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