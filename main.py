import contextlib
import discord
from discord.ext import commands
import asyncio
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from datetime import datetime, timedelta, timezone

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = AutoShardedBot(command_prefix='v!', intents=intents)

bot.remove_command("help")


bot.remove_command('help')

presence_messages = [
    "♚ /help ♚",
]

async def change_presence():
    while True:
        for message in presence_messages:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=message, url='https://www.twitch.tv/example'))
            await asyncio.sleep(300) 

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    bot.loop.create_task(change_presence())

    await bot.load_extension("farm.farm")
    await bot.load_extension("farm.animal")
    await bot.load_extension("farm.barn")
    await bot.load_extension("farm.campfire")
    await bot.load_extension("farm.waterwell")
    await bot.load_extension("farm.plantshop")
    await bot.load_extension("farm.buyseeds")
    await bot.load_extension("farm.waterplant")
    await bot.load_extension("farm.fertilizeplant")
    await bot.load_extension("farm.plantcondition")
    await bot.load_extension("farm.collect")

    await bot.load_extension("town.appliance")
    await bot.load_extension("town.busking")
    await bot.load_extension("town.fish")
    await bot.load_extension("town.gamble")
    await bot.load_extension("town.invest")
    await bot.load_extension("town.lottery")
    await bot.load_extension("town.mine")
    await bot.load_extension("town.pickpocket")
    await bot.load_extension("town.rob")
    await bot.load_extension("town.shoplift")
    await bot.load_extension("town.tasks")
    await bot.load_extension("town.trivia")
    await bot.load_extension("town.townstats")

    await bot.load_extension("crypto.cryptoprice")
    await bot.load_extension("crypto.cryptonews")
    await bot.load_extension("crypto.cryptocal")

    await bot.load_extension("cogs.help")

    await bot.load_extension("games.coinflip")
    await bot.load_extension("games.dog")
    await bot.load_extension("games.snipe")
    await bot.load_extension("games.droll")
    await bot.load_extension("games.joke")
    await bot.load_extension("games.reactiongame")

    await bot.load_extension("partners.partnersetup")
    await bot.load_extension("partners.pembed")
    await bot.load_extension("partners.partnerlead")

    await bot.load_extension("stats.botstats")
    await bot.load_extension("stats.serverstats")
    await bot.load_extension("stats.weeklyjoins")
    await bot.load_extension("stats.votelead")

    await bot.load_extension("messaging.leaderboard")
    await bot.load_extension("messaging.messagecount")
    await bot.load_extension("messaging.cleaderboard")

    await bot.load_extension("mods.ban")
    await bot.load_extension("mods.roleall")
    await bot.load_extension("mods.timeout")
    await bot.load_extension("mods.unban")
    await bot.load_extension("mods.kick")
    await bot.load_extension("mods.warn")
    await bot.load_extension("mods.swarnings")
    await bot.load_extension("mods.cwarnings")
    await bot.load_extension("mods.wleaderboard")

    await bot.load_extension("setups.ticket")
    await bot.load_extension("setups.logging")
    await bot.load_extension("setups.setbump")

    await bot.load_extension("welcome.ping")

    await bot.load_extension("automod.autodb")
    await bot.load_extension("automod.badwords")
    await bot.load_extension("automod.caps")
    await bot.load_extension("automod.characterspam")
    await bot.load_extension("automod.emoji")
    await bot.load_extension("automod.images")
    await bot.load_extension("automod.invite")
    await bot.load_extension("automod.link")
    await bot.load_extension("automod.maxcharacters")
    await bot.load_extension("automod.mention")
    await bot.load_extension("automod.spam")
    await bot.load_extension("automod.automod")

    await bot.tree.sync() 

@bot.event
async def on_command_error(ctx, error):  # sourcery skip: low-code-quality
        try:
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(description="`Invalid command.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(description="`You are missing a required argument.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.BadArgument):
                embed = discord.Embed(description="`Invalid argument.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.CommandOnCooldown):
                cooldown_time = round(error.retry_after, 2)
                if cooldown_time < 60:
                    cooldown_text = f"{cooldown_time} seconds"
                elif cooldown_time < 3600:
                    cooldown_text = f"{cooldown_time // 60} minutes"
                else:
                    cooldown_text = f"{cooldown_time // 3600} hours"

                embed = discord.Embed(description=f"`This command is on cooldown. Try again in {cooldown_text}.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.MissingPermissions):
                embed = discord.Embed(description="`You do not have permission to use this command.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.BotMissingPermissions):
                embed = discord.Embed(description="`I do not have permission to perform this command.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)
            elif isinstance(error, commands.NoPrivateMessage):
                embed = discord.Embed(description="`This command cannot be used in private messages.`", color=0x2a2d31)
                error_msg = await ctx.send(embed=embed)

            await asyncio.sleep(60)
            with contextlib.suppress(discord.errors.NotFound):
                await ctx.message.delete()
                await error_msg.delete()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")   


bot.run('')