import sqlite3
from discord.ext import commands
import discord
from discord.ext.commands import BucketType, CommandOnCooldown

class Collect(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database

    @commands.hybrid_command()
    @commands.cooldown(1, 86400, BucketType.user)  # 86400 seconds = 24 hours
    async def collect(self, ctx):  # sourcery skip: hoist-similar-statement-from-if, hoist-statement-from-if
        """Collect coins from your animals!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            coins = user[1]
            animals = user[2]
            new_coins = coins + (animals * 100)  # Each animal generates 100 coins
            c.execute("UPDATE farm SET coins = ? WHERE user_id=?", (new_coins, user_id))
            conn.commit()
            image_url = f"https://vashly.com/wp-content/uploads/2023/06/{animals}.png"
            embed = discord.Embed(title="Collection Successful", description=f"`You have collected {animals * 100} coins!`", color=0x2a2d31)
            embed.set_image(url=image_url)
            embed.set_footer(text="View documentation for all commands.")
        else:
            embed = discord.Embed(title="Collection Failed", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

    @collect.error
    async def collect_error(self, ctx, error):
        if not isinstance(error, CommandOnCooldown):
            raise error
        embed = discord.Embed(title="Collection Failed", description="This command is on a 24-hour cooldown!`", color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)


async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(Collect(bot, database))
