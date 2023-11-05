import discord
from discord.ext import commands
import sqlite3
import random
import time

class Rob(commands.Cog):
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
        self.user_last_rob_time = {}

    @commands.hybrid_command()
    async def rob(self, ctx):  # sourcery skip: hoist-similar-statement-from-if
        """Rob a bank to gain coins!"""
        embed = discord.Embed(title="Robbery Results", color=0x2a2d31)
        current_time = time.time()
        last_rob_time = self.user_last_rob_time.get(ctx.author.id, 0)
        if current_time - last_rob_time < 86400:  # 86400 seconds = 1 day
            embed.description = "`You can only rob once every 24 hours!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        chance_of_success = random.uniform(0.01, 0.5)
        if random.random() < chance_of_success:
            amount = random.randint(100, 1000)  # Generate a random amount between 100 and 1000
            self.cursor.execute(
                "UPDATE users SET income=income+? WHERE discord_id=?",
                (amount, str(ctx.author.id)),
            )
            self.connection.commit()
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.description = f"You successfully robbed the bank and stole `{amount}` coins! Your new balance is `{self.get_user_balance(ctx.author.id)}` coins."
            embed.set_footer(text="View documentation for all commands.")
        else:
            fine = 200
            try:
                self.cursor.execute(
                    "UPDATE users SET income=income-?, happiness=happiness-1, population=population-1 WHERE discord_id=?",
                    (fine, str(ctx.author.id)),
                )
                self.connection.commit()
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                embed.description = f"You were caught attempting to rob the bank and fined `{fine}` coins! Your new balance is `{self.get_user_balance(ctx.author.id)}` coins."
                embed.set_footer(text="View documentation for all commands.")
            except Exception as e:
                print(f"Error updating user balance: {e}")
                embed.description = "`Sorry, there was an error updating your balance. Please try again later`"
                embed.set_footer(text="View documentation for all commands.")

        self.user_last_rob_time[ctx.author.id] = current_time
        await ctx.send(embed=embed)

    def get_user_balance(self, discord_id):
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (str(discord_id),))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(Rob(bot))
