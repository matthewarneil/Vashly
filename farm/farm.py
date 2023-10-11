import sqlite3
import asyncio
import discord
from discord.ext import commands, tasks

class FarmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = 'farm.db'
        self.create_table()
        self.idle_time_update.start()

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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (message.author.id,))
        user = c.fetchone()
        if user is None:
            c.execute("INSERT INTO farm VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 600)", (message.author.id,))
        else:
            new_idle_time = min(600 + sum(user[2:7])*60, 600)
            c.execute("UPDATE farm SET idle_time = ? WHERE user_id = ?", (new_idle_time, message.author.id))
        conn.commit()
        conn.close()

    @tasks.loop(minutes=1)
    async def idle_time_update(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm")
        users = c.fetchall()
        for user in users:
            if user[11] > 0:  # check if user still has remaining idle time
                max_idle_time = 600 + sum(user[2:7])*60
                new_idle_time = max(0, user[11] - 60)
                if new_idle_time > 0:
                    c.execute("UPDATE farm SET idle_time = ?, coins = coins + 1 WHERE user_id = ?", (new_idle_time, user[0]))
                else:
                    c.execute("UPDATE farm SET idle_time = 0 WHERE user_id = ?", (user[0],))
        conn.commit()
        conn.close()

    @idle_time_update.before_loop
    async def before_idle_time_update(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_command()
    async def farm(self, ctx):
        """View your farm!"""
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (ctx.author.id,))
        user = c.fetchone()
        if user is not None:
            embed = discord.Embed(title="Farm", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.add_field(name="Coins", value=f"{user[1]:,}", inline=True)
            embed.add_field(name="Animals", value=user[2], inline=True)
            embed.add_field(name="Barns", value=user[3], inline=True)
            embed.add_field(name="Campfires", value=user[4], inline=True)
            embed.add_field(name="Water Wells", value=user[5], inline=True)
            embed.add_field(name="Plants", value=user[6], inline=True)
            embed.add_field(name="Idle Time", value=f"{user[11] // 60} / {600 // 60 + sum(user[2:7])} minutes", inline=False)
            embed.set_footer(text="View documentation for all commands.")

            # Add animal image
            animal = user[2]
            image_url = f"https://vashly.com/wp-content/uploads/2023/06/{animal}.png"
            embed.set_image(url=image_url)

            await ctx.send(embed=embed)
        else:
            await ctx.send("`Kindly wait for one minute before attempting to use the command again, as your farm is currently loading.`")
        conn.close()



async def setup(bot):
    await bot.add_cog(FarmCog(bot))
