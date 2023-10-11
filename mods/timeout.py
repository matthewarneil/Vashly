import discord
from discord.ext import commands
from datetime import timedelta

class TimeoutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(moderate_members=True)
    @commands.hybrid_command()
    async def mute(self, ctx, member: discord.Member, minutes: int, *, reason: str = None):
        """Timeouts a user for a given number of minutes.
        Parameters
        -----------
        member: member
            Select the member to timeout.

        Parameters
        -----------
        minutes: minutes
            Select the time in minutes to time the user out.

        Parameters
        -----------
        reason: reason
            Write the reason for the timeout.   
        
        """
        if minutes > 60 * 24 * 28:  # 28 days in minutes
            await ctx.send("`The number of minutes cannot exceed 40320 (28 days).`", ephemeral=True)
            return

        await member.timeout(timedelta(minutes=minutes), reason=reason)
        await ctx.send(f"**{member.mention} has been timed out for {minutes} minutes.**", ephemeral=True)

    @mute.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("`You don't have permission to use this command.`", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("`Invalid argument. Please make sure to mention a user and provide a valid number of minutes.`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TimeoutCog(bot))
