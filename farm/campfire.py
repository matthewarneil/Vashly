import sqlite3
import asyncio
import aiohttp
import discord
from discord.ext import commands

class Campfire(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS farm (
                        user_id INTEGER PRIMARY KEY,
                        coins INTEGER,
                        animals INTEGER,
                        barns INTEGER,
                        campfires INTEGER,
                        water_wells INTEGER,
                        plants INTEGER,
                        seed_type INTEGER,
                        water_level INTEGER,
                        fertilizer_level INTEGER,
                        last_cared datetime,
                        idle_time INTEGER
                        )''')
        conn.commit()
        conn.close()

    @commands.hybrid_command()
    async def buycampfire(self, ctx):
        """Buy a campfire for your farm!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            if user[4] >= 1:
                embed = discord.Embed(title="Transaction Failed", description="`You already own a campfire.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_balance = user[1] - 50000
            if new_balance < 0:
                embed = discord.Embed(title="Transaction Failed", description="`You don't have enough coins. You need 50,000.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_campfire_count = user[4] + 1
            c.execute("UPDATE farm SET coins = ?, campfires = ? WHERE user_id=?", (new_balance, new_campfire_count, user_id))
            conn.commit()
            image_url = "https://vashly.com/wp-content/uploads/2023/06/campfire-1.png"
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        embed = discord.Embed(title="Transaction Failed", description="`Could not download file. Contact Support.`", color=0x2a2d31)
                        embed.set_footer(text="View documentation for all commands.")
                        await ctx.send(embed=embed)
                        return
                    data = await resp.read()
                    await session.close()
            embed = discord.Embed(title="Transaction Successful", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_image(url=image_url)
        else:
            embed = discord.Embed(title="Transaction Failed", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(Campfire(bot, database))
