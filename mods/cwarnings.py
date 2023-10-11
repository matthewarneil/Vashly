import discord
from discord.ext import commands

import sqlite3


class ClearWarnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('warn.db')
        self.cursor = self.conn.cursor()

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def cwarnings(self, ctx, member: discord.Member):
        """Clears all warnings of a user from the database in the current guild.
        
        Parameters
        -----------
        member: member
            Select the member to clear the warnings.
        
        
        """
        # delete all warnings of the user in the current guild from the database
        self.cursor.execute('''
            DELETE FROM warnings
            WHERE user_id=? AND guild_id=?
        ''', (member.id, ctx.guild.id))
        self.conn.commit()

        # send a message indicating that the warnings have been cleared and delete the command message
        embed = discord.Embed(title='Warnings Cleared', description=f'All warnings of {member.mention} in this guild have been cleared.', color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ClearWarnings(bot))
