import sqlite3
import discord
from discord.ext import commands
from datetime import datetime

class BuySeed(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database

    @commands.hybrid_command()
    async def buyseed(self, ctx, seed: int):
        """Buy Seeds for your farm!

        Parameters
        -----------
        seed: seed
            Select the desired seed for purchase (1-9) from the available options displayed in the plant shop.
        """
   
        if seed < 1 or seed > 9:
            embed = discord.Embed(title="Transaction Failed", description="`Invalid seed type. Choose a number between 1 and 9.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        user_id = ctx.message.author.id
        seed_cost = seed * 1000
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            if user[7] != 0:
                embed = discord.Embed(title="Transaction Failed", description="`You already have a seed planted.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_balance = user[1] - seed_cost
            if new_balance < 0:
                embed = discord.Embed(title="Transaction Failed", description="`You don't have enough coins. View the plant shop.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            c.execute("UPDATE farm SET coins = ?, seed_type = ?, last_cared = ? WHERE user_id=?", (new_balance, seed, datetime.now(), user_id))
            conn.commit()
            embed = discord.Embed(title="Transaction Successful", description=f"`You've bought a type {seed} seed.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_image(url="https://vashly.com/wp-content/uploads/2023/06/Seeds.png")
        else:
            embed = discord.Embed(title="Transaction Failed", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(BuySeed(bot, database))
