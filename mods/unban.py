import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MemberConverter
from discord.utils import get

class MemberID(MemberConverter):
    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.hybrid_command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """ Unban a user. 
        
        Parameters
        -----------
        member: member
            Write the userID to unban.

        Parameters
        -----------
        reason: reason
            Reason for unban.
        
        """
        try:
            await ctx.guild.unban(discord.Object(id=member), reason=f"{ctx.author}")
            embed = discord.Embed(
                color=0x2F3136
            )
            embed.set_author(name="User Unbanned")
            embed.add_field(name="Unbanned Member", value=f"<@{member}>", inline=False)
            embed.add_field(name="Unban Reason", value=reason, inline=False)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error unbanning user: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
