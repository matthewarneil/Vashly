import discord
from discord.ext import commands
import sqlite3

class PartnershipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("partnership.db")
        self.c = self.conn.cursor()

    @commands.hybrid_command()
    async def partnerlead(self, ctx):
        """Partnership Leaderboard"""
        guild_id = ctx.guild.id
        self.c.execute("""
            SELECT users.user_id, SUM(users.points) as total_points
            FROM users
            JOIN partnership_channels ON partnership_channels.guild_id = users.guild_id
            WHERE users.guild_id = ?
            GROUP BY users.user_id
            ORDER BY total_points DESC
            LIMIT 10
        """, (guild_id,))
        results = self.c.fetchall()

        # create the leaderboard message
        leaderboard = []
        for i, result in enumerate(results):
            user_id, total_points = result
            if user := self.bot.get_user(user_id):
                leaderboard.append(f"`{i+1})` {user.mention} (ID: {user_id}): `{total_points}` ")

        # create the embed message
        embed = discord.Embed(title="Partnership Leaderboard", color=0x2a2d31)
        embed.description = "\n".join(leaderboard)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(PartnershipCog(bot))
