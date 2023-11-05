import discord
from discord.ext import commands
import sqlite3
import random
import time

class DailyTasks(commands.Cog):
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
        self.user_last_tasks_time = {}

    def user_exists(self, discord_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (discord_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, discord_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (discord_id,))
        self.connection.commit()

    @commands.hybrid_command()
    async def tasks(self, ctx):
        """Complete daily tasks for coins. Can only be used once per day."""
        embed = discord.Embed(title="Daily Tasks Results", color=0x2a2d31)
        # Check if the user has already used the command within the last day
        current_time = time.time()
        last_tasks_time = self.user_last_tasks_time.get(ctx.author.id, 0)  # get the last time the command was used by this user
        if current_time - last_tasks_time < 86400: # 86400 seconds = 1 day
            embed.description = "`You can only use the tasks command once per day!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        # Generate a random amount of coins between 100 and 1000
        amount = random.randint(100, 1000)

        # Update user's balance, happiness, and population
        try:
            self.cursor.execute(
                "UPDATE users SET income=income+?, happiness=happiness+1, population=population+1 WHERE discord_id=?",
                (amount, str(ctx.author.id)),
            )
            self.connection.commit()
        except Exception as e:
            print(f"Error updating user balance: {e}")
            embed.description = "`Sorry, there was an error updating your balance. Please try again later`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        # Update the last tasks time for this user
        self.user_last_tasks_time[ctx.author.id] = current_time

        # Send a message with the result of the daily tasks
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.description = f"You completed your daily tasks and earned `{amount}` coins! Your new balance is `{self.get_user_balance(ctx.author.id)}` coins."
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

    def get_user_balance(self, discord_id):
        """Get the current balance of a user."""
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (str(discord_id),))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(DailyTasks(bot))
