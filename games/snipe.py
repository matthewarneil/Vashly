import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.sniped_messages[message.channel.id] = message

    @commands.hybrid_command()
    async def snipe(self, ctx):
        """Fetch the last deleted message."""
        channel = ctx.channel
        if channel.id in self.sniped_messages:
            message = self.sniped_messages[channel.id]
            embed = discord.Embed(
                description=f"**{message.author.mention} said: {message.content}**",
                color=0x2a2d31
            )
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("`No recently deleted message found.`")

async def setup(bot):
    await bot.add_cog(Snipe(bot))
