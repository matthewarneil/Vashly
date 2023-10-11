import discord
from discord.ext import commands


class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        """Kicks a member from the server.
        
        Parameters
        -----------
        reason: reason
            The kick reason.

        Parameters
        -----------
        member: member
            The member you want to kick.
        
        """
        try:
            await member.kick(reason=reason)

            embed = discord.Embed(color=0x2a2d31)
            embed.set_author(name="User Kicked")
            embed.add_field(name="Kicked Member", value=f"{member.mention}", inline=False)
            embed.add_field(name="Kick Reason", value=reason, inline=False)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"Failed to kick the member. Error: {e}", color=0x2a2d31)
            await ctx.send(embed=embed)


async def setup(bot):
   await bot.add_cog(Kick(bot))
