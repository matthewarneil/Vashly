import discord
from discord.ext import commands
import sqlite3

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('warn.db')
        self.cursor = self.conn.cursor()

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def wleaderboard(self, ctx):
        """Displays the top 10 most warned users in the current guild."""
        # retrieve warnings for the current guild from the database and display a leaderboard
        self.cursor.execute('''
            SELECT user_id, COUNT(*) AS warning_count
            FROM warnings
            WHERE guild_id=?
            GROUP BY user_id
            ORDER BY warning_count DESC
            LIMIT 10
        ''', (ctx.guild.id,))
        if rows := self.cursor.fetchall():
            leaderboard = '\n'.join([f'`{idx})` **{self.bot.get_user(row[0]).mention if self.bot.get_user(row[0]) else "Unknown User"}** (ID: {row[0]}) - `{row[1]} warnings`' for idx, row in enumerate(rows, start=1)])
            embed = discord.Embed(title='Most Warned Users', description=leaderboard, color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        else:
            embed = discord.Embed(title='Most Warned Users', description='No warnings found.', color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))
