import discord
from discord.ext import commands
import sqlite3
import random
import time

class Shoplift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('town.db')
        self.cursor = self.connection.cursor()
        self.user_last_shoplift_time = {}

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    @commands.hybrid_command()
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 minutes cooldown per user
    async def shoplift(self, ctx):
        """Attempt to shoplift and gain income or get caught and fined."""
        if not self.user_exists(ctx.author.id):
            return await ctx.send("You are not in the database!")
        embed = discord.Embed(title="Shoplift Results", color=0x2a2d31)
        current_time = time.time()
        last_shoplift_time = self.user_last_shoplift_time.get(ctx.author.id, 0)
        if current_time - last_shoplift_time < 300:  # 300 seconds = 5 minutes
            embed.description = "`You can only shoplift once every 5 minutes!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        chance = random.random()  # Generate a random chance between 0 and 1
        if chance <= 0.8:  # 80% chance to successfully shoplift and gain coins
            income_gained = random.randint(10, 20)
            try:
                self.cursor.execute(
                    "UPDATE users SET income=income+? WHERE discord_id=?",
                    (income_gained, ctx.author.id),
                )
                self.connection.commit()
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                embed.description = f"You successfully shoplifted and gained `{income_gained}` coins! Your new income is `{self.get_user_income(ctx.author.id)}` coins."
                embed.set_footer(text="View documentation for all commands.")
            except Exception as e:
                print(f"Error updating user balance: {e}")
                embed.description = "`Sorry, there was an error updating your income. Please try again later`"
                embed.set_footer(text="View documentation for all commands.")
        else:  # 20% chance to get caught and fined
            fine = 150
            try:
                self.cursor.execute(
                    "UPDATE users SET income=income-?, population=population-1, happiness=happiness-1 WHERE discord_id=?",
                    (fine, ctx.author.id),
                )
                self.connection.commit()
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                embed.description = f"You were caught while shoplifting and fined `{fine}` coins! Your new income is `{self.get_user_income(ctx.author.id)}` coins."
                embed.set_footer(text="View documentation for all commands.")
            except Exception as e:
                print(f"Error updating user balance: {e}")
                embed.description = "`Sorry, there was an error updating your income. Please try again later`"
                embed.set_footer(text="View documentation for all commands.")

        self.user_last_shoplift_time[ctx.author.id] = current_time
        await ctx.send(embed=embed)

    def get_user_income(self, user_id):
        """Get the current income of a user."""
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(Shoplift(bot))
