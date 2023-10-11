import sqlite3
import asyncio
import aiohttp
import discord
from discord.ext import commands

class PlantShop(commands.Cog):
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
    async def plantshop(self, ctx):
        """View what seeds and plants to buy!"""
        embed = discord.Embed(title="Plant Shop", color=0x2a2d31)
        embed.set_image(url="https://vashly.com/wp-content/uploads/2023/06/plantshop.png")
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(PlantShop(bot, database))
