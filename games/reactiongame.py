import discord
from discord.ext import commands
import random
import asyncio

class ReactionGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def reactiongame(self, ctx, member: discord.Member):
        """Starts a reaction game with the specified user.
         Parameters
        -----------
        member: member
            Choose who you want to play with!
        """
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
        correct_reaction = random.choice(reactions)

        embed = discord.Embed(title="Reaction Game", color=0x2a2d31)
        embed.set_author(name=f"{ctx.author.display_name} vs {member.display_name}")
        embed.add_field(
            name="Instructions",
            value="**Please let all reactions to load onto the message before reacting!**\nReact to this message with the correct reaction to win!",
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Game ends in one minute.")

        message = await ctx.send(f"{ctx.author.mention} has started a reaction game with {member.mention}!")
        await message.edit(embed=embed)

        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(reaction, user):
            if reaction.message != message or user != member:
                return False
            if str(reaction.emoji) == correct_reaction:
                return True
            else:
                raise ValueError("Selected the wrong reaction")

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            await message.remove_reaction(reaction, user)

            embed.set_author(name=f"{user.display_name} won the game!")
            embed.set_footer(text="")
            await message.edit(embed=embed)

        except asyncio.TimeoutError:
            embed.set_author(name=f"{member.display_name} didn't react in time.")
            embed.set_footer(text="")
            await message.edit(embed=embed)

        except ValueError:
            embed.set_author(name=f"{member.display_name} selected the wrong reaction.")
            embed.set_footer(text="")
            await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(ReactionGameCog(bot))
