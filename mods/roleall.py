import discord
from discord.ext import commands
import asyncio

class RoleAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def roleall(self, ctx, role: discord.Role):
        """
        Assigns a selected role to all users, humans, or bots in the server.

        Parameters
        -----------
        role: role
            Select the role you want give to users/bots.
        """
        class TargetMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="All", value="all"),
                    discord.SelectOption(label="Humans", value="humans"),
                    discord.SelectOption(label="Bots", value="bots")
                ]
                super().__init__(placeholder="Select a target", options=options)

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                target = self.values[0]

                member_count = 0
                if target == "all":
                    members = ctx.guild.members
                    member_count = len(members)
                elif target == "humans":
                    members = [member for member in ctx.guild.members if not member.bot]
                    member_count = len(members)
                elif target == "bots":
                    members = [member for member in ctx.guild.members if member.bot]
                    member_count = len(members)

                await ctx.send(f"**Assigning role '{role.name}' to {member_count} members. This might take a while...**", ephemeral=True)

                failed_count = 0

                for member in members:
                    try:
                        await member.add_roles(role)

                        # Rate limit handling
                        if (member_count - failed_count) % 10 == 0:
                            await asyncio.sleep(1)  # Sleep for 1 second to avoid rate limits

                    except discord.Forbidden:
                        failed_count += 1

                await ctx.send(f"**Successfully assigned role '{role.name}' to {member_count - failed_count} members.**", ephemeral=True)

                if failed_count > 0:
                    await ctx.send(f"**Failed to assign role to {failed_count} members.**", ephemeral=True)

        view = discord.ui.View()
        view.add_item(TargetMenu())

        await ctx.send("**Please select a target option:**", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleAll(bot))
