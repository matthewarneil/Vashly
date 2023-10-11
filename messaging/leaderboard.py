import discord
from discord.ext import commands
import random
import asyncio
import sqlite3

conn = sqlite3.connect('messaging.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        user_id INTEGER,
        guild_id INTEGER,
        message_count INTEGER,
        PRIMARY KEY (user_id, guild_id)
    )
''')
conn.commit()

def get_cursor():
    conn = sqlite3.connect('messaging.db')
    cursor = conn.cursor()
    return cursor

class Leaderboard(commands.Cog):
    def __init__(self, bot, cursor):
        self.bot = bot
        self.cursor = cursor

    @commands.hybrid_command()
    async def leaderboard(self, ctx):
        """Displays the top 10 users by message count in the current guild."""
        # get the top 10 users by message count in the current guild
        self.cursor.execute('''
            SELECT user_id, message_count
            FROM messages
            WHERE guild_id = ?
            ORDER BY message_count DESC
            LIMIT 10
        ''', (ctx.guild.id,))
        rows = self.cursor.fetchall()

        # create the leaderboard message
        leaderboard = []
        for i, row in enumerate(rows):
            user_id, message_count = row
            member = ctx.guild.get_member(user_id)
            if member is None:
                if not str(user_id).isdigit():
                    username = f'user{user_id}'
                    user_tag = f'<@{user_id}>'
                    leaderboard.append(f'`{i+1})` {username} ({user_tag}): `{message_count}`')

            elif not member.display_name.isdigit():
                username = member.display_name
                user_tag = member.mention
                leaderboard.append(f'`{i+1})` {username} ({user_tag}): `{message_count}`')
        embed = discord.Embed(title='Message Leaderboard', description='\n'.join(leaderboard), color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    cursor = get_cursor()  # Replace with your own function to get a cursor
    await bot.add_cog(Leaderboard(bot, cursor))
    await asyncio.sleep(0.2)
