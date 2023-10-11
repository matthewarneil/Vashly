import discord
import random
import sqlite3
from discord.ext import commands

class cleaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('messaging.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                user_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                message_count INTEGER
            )
        ''')
        self.conn.commit()

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def cleaderboard(self, ctx):
        """Clears the message leaderboard for the current guild."""
        # clear the leaderboard for the current guild
        self.cursor.execute('''
            DELETE FROM messages
            WHERE guild_id = ?
        ''', (ctx.guild.id,))
        self.conn.commit()

        embed = discord.Embed(title='Message Leaderboard Cleared', color=0x2a2d31)
        embed.add_field(name='Success', value='The message leaderboard has been cleared.')
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(cleaderboard(bot))
