import discord
from discord.ext import commands
import sqlite3
import random
import time

class Mine(commands.Cog):
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
        self.user_last_mine_time = {}  # dictionary to store the last time the command was used by each user

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (user_id,))
        self.connection.commit()

    @commands.hybrid_command()
    async def mine(self, ctx):
        """Mine virtual resources for coins. Can only be used once every 30 minutes."""
        embed = discord.Embed(title="Mining Results", color=0x2a2d31)
        # Check if the user has already used the command within the last 30 minutes
        current_time = time.time()
        last_mine_time = self.user_last_mine_time.get(ctx.author.id, 0)  # get the last time the command was used by this user
        if current_time - last_mine_time < 1800: # 1800 seconds = 30 minutes
            embed.description = "`You can only use the mine command once every 30 minutes!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        # Generate a random amount of resources between 1 and 10
        resources = random.randint(1, 10)

        # Generate a random amount of coins based on the amount of resources
        coins = resources * random.randint(10, 20)

        # Update user's balance
        self.cursor.execute(
            "UPDATE users SET income=income+?, happiness=happiness-1, population=population+1 WHERE discord_id=?",
            (coins, str(ctx.author.id)),
        )
        self.connection.commit()

        # Update the last mine time for this user
        self.user_last_mine_time[ctx.author.id] = current_time

        # Send a message with the result of the mining
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.description = f"You mined `{resources}` resources and earned `{coins}` coins! Your new balance is `{self.get_user_balance(ctx.author.id)}` coins."
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

    def get_user_balance(self, user_id):
        """Get the current balance of a user."""
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (str(user_id),))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(Mine(bot))
