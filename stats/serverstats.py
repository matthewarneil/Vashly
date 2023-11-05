import discord
from discord.ext import commands

class ServerStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def serverstats(self, ctx):
        """Displays server statistics."""
        # Get the server's stats, ignoring bots
        member_count = len([member for member in ctx.guild.members if not member.bot])
        channel_count = len(ctx.guild.channels)
        role_count = len(ctx.guild.roles)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        boost_count = ctx.guild.premium_subscription_count
        boost_level = ctx.guild.premium_tier
        owner = ctx.guild.owner.display_name

        # Create the embed
        embed = discord.Embed(title='Server Statistics', description='`Here are some statistics about this server:`', color=0x2a2d31)
        embed.add_field(name='Owner', value=owner, inline=True)
        embed.add_field(name='Members', value=member_count, inline=True)
        embed.add_field(name='Channels', value=channel_count, inline=True)
        embed.add_field(name='Text Channels', value=text_channels, inline=True)
        embed.add_field(name='Voice Channels', value=voice_channels, inline=True)
        embed.add_field(name='Categories', value=categories, inline=True)
        embed.add_field(name='Roles', value=role_count, inline=True)
        embed.add_field(name='Boost Count', value=boost_count, inline=True)
        embed.add_field(name='Boost Level', value=f'{boost_level}', inline=True)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        # Send the embed to the channel
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerStatsCog(bot))
