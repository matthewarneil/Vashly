import sqlite3
from discord import Embed
from discord.ext import commands
import discord

class Upgrade(commands.Cog):
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

    def user_exists(self, discord_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (discord_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, discord_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (discord_id,))
        self.connection.commit()

    @commands.hybrid_command()
    async def buyappliance(self, ctx):
        """Spend 100,000 coins to upgrade your house!"""
        discord_id = ctx.author.id
        if not self.user_exists(discord_id):
            self.add_user(discord_id)

        self.cursor.execute("SELECT income, infrastructure FROM users WHERE discord_id=?", (discord_id,))
        income, current_level = self.cursor.fetchone()

        if income >= 100000 and current_level < 18:
            new_level = current_level + 1
            self.cursor.execute("UPDATE users SET income=income-100000, infrastructure=? WHERE discord_id=?", (new_level, discord_id,))
            self.connection.commit()

            embed = Embed(
                title="Upgraded!",
                description=f"`You have upgraded your town to level {new_level}!`",
                color=0x2a2d31
            )
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_image(url=f"https://vashly.com/wp-content/uploads/2023/06/house-{new_level}.png")
        elif current_level >= 18:
            embed = Embed(
                title="Maximum level reached",
                description="`Your town has reached the maximum level.`",
                color=0x2A2D31,
            )
            embed.set_footer(text="View documentation for all commands.")
        else:
            embed = Embed(
                title="Insufficient coins",
                description="`You don't have enough coins to upgrade.`",
                color=0x2A2D31,
            )
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Upgrade(bot))
