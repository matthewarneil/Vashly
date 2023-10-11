import discord
import random
import sqlite3
from discord.ext import commands

class SWarnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('warn.db')
        self.cursor = self.conn.cursor()

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def swarnings(self, ctx, member: discord.Member):
        """Searches for warnings of a user in the current guild.
        Parameters
        -----------
        member: member
            Select the member to search.
        
        
        """
        # get the user's warnings in the current guild from the database
        self.cursor.execute('''
            SELECT id, moderator_id, reason
            FROM warnings
            WHERE user_id = ? AND guild_id = ?
        ''', (member.id, ctx.guild.id))
        results = self.cursor.fetchall()

        embed = discord.Embed(title='Search Results', color=0x2a2d31)
        embed.set_author(name=f'Warnings for {member.name}', icon_url=member.avatar.url)
        if len(results) > 0:
            for result in results:
                embed.add_field(name='Warning', value=f'Moderator: <@{result[1]}> \nReason: {result[2]}', inline=False)
                embed.set_footer(text="View documentation for all commands.")
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        else:
            embed.description = 'No warnings found for this user in this guild.'
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(SWarnings(bot))
