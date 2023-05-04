import discord
from discord.ext import commands
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
     
        
    def sort_by_mastery(self, x):
        return x[1][1]
       
        
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
                summoner = input[0].replace(" ", "%20") 
                count = input[1]
                url = self.gameAPI_url + "/mastery/" + summoner+"/"+count
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
                summoner = input[0].replace(" ", "%20") 
                ranked_type = input[1].upper()  # Clean up the input, make it all uppercase
                url = self.gameAPI_url + "/rank/" + summoner + "/" + ranked_type
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



async def setup(bot, url):
    """Adds this cog to the bot, meaning that the commands in the League class can be used by the bot/users

        Args:
            bot (discord.Bot): The bot object to have the cog added to
    """    
    await bot.add_cog(league(bot, gameAPI_url=url))
    print("League is online!")
        