import discord
from discord.ext import commands
import sqlite3
import random
import time

class Busking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('town.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                discord_id INTEGER PRIMARY KEY,
                                population INTEGER NOT NULL,
                                income INTEGER NOT NULL,
                                happiness INTEGER NOT NULL,
                                infrastructure INTEGER NOT NULL
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS buildings (
                                id INTEGER PRIMARY KEY,
                                discord_id INTEGER,
                                building_type TEXT NOT NULL,
                                building_level INTEGER NOT NULL,
                                FOREIGN KEY(discord_id) REFERENCES users(discord_id)
                            )""")
        self.user_last_busking_time = {}

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (user_id,))
        self.connection.commit()

    @commands.hybrid_command()
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 minutes cooldown per user
    async def busking(self, ctx):
        """Perform a busking session to gain coins."""
        embed = discord.Embed(title="Busking Session", color=0x2a2d31)
        current_time = time.time()
        last_busking_time = self.user_last_busking_time.get(ctx.author.id, 0)
        if current_time - last_busking_time < 300:  # 300 seconds = 5 minutes
            embed.description = "`You can only busk once every 5 minutes!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        coins_gained = random.randint(10, 20)
        try:
            self.cursor.execute(
                "UPDATE users SET income=income+?, happiness=happiness+1, population=population+1 WHERE discord_id=?",
                (coins_gained, ctx.author.id),
            )
            self.connection.commit()
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.description = f"You performed a busking session and earned `{coins_gained}` coins! Your new income is `{self.get_user_income(ctx.author.id)}` coins."
            embed.set_footer(text="View documentation for all commands.")
        except Exception as e:
            print(f"Error updating user income: {e}")
            embed.description = "`Sorry, there was an error updating your income. Please try again later`"
            embed.set_footer(text="View documentation for all commands.")

        self.user_last_busking_time[ctx.author.id] = current_time
        await ctx.send(embed=embed)

    def get_user_income(self, user_id):
        """Get the current income of a user."""
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(Busking(bot))
