import sqlite3
import asyncio
import aiohttp
import discord
from discord.ext import commands

class WaterWell(commands.Cog):
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
    async def buywaterwell(self, ctx):
        """Buy a water well for your farm!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            if user[5] >= 1:
                embed = discord.Embed(title="Transaction Failed", description="`You already own a water well.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_balance = user[1] - 70000
            if new_balance < 0:
                embed = discord.Embed(title="Transaction Failed", description="`You don't have enough coins. You need 70,000.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_water_well_count = user[5] + 1
            c.execute("UPDATE farm SET coins = ?, water_wells = ? WHERE user_id=?", (new_balance, new_water_well_count, user_id))
            conn.commit()
            image_url = "https://vashly.com/wp-content/uploads/2023/06/Water-Well.png"
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
    await bot.add_cog(WaterWell(bot, database))
