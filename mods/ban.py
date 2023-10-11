import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        """Bans a user from the server using a mention.
        Parameters
        -----------
        user: user
            The user/id you want to ban.
        
        Parameters
        -----------
        reason: reason
            The ban reason.
        
        """
        try:
            await ctx.guild.ban(user, reason=reason)
            embed = discord.Embed(color=0x2a2d31)
            embed.set_author(name="User Banned")
            embed.add_field(name="Banned Member", value=f"{user.mention}", inline=False)
            embed.add_field(name="Ban Reason", value=reason, inline=False)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"Failed to ban the user. Error: {e}", color=0x2a2d31)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ban(bot))
