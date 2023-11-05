import discord
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, timezone
from discord.ext import commands

class WeeklyJoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def weeklyjoins(self, ctx):
        """Shows the servers weekly joins compared to last weeks."""
        current_date = datetime.now(timezone.utc).date()

        # Calculate the start and end dates of the current week
        current_week_start = current_date - timedelta(days=current_date.weekday())
        current_week_end = current_week_start + timedelta(days=6)

        # Calculate the start and end dates of the previous week
        previous_week_start = current_week_start - timedelta(days=7)
        previous_week_end = current_week_start - timedelta(days=1)

        # Get the list of members who joined in the current week
        current_week_joins = [member for member in ctx.guild.members if current_week_start <= member.joined_at.date() <= current_week_end]

        # Get the list of members who joined in the previous week
        previous_week_joins = [member for member in ctx.guild.members if previous_week_start <= member.joined_at.date() <= previous_week_end]

        # Calculate the number of new joins each day for the current and previous weeks
        current_week_counts = np.zeros((7,), dtype=int)
        previous_week_counts = np.zeros((7,), dtype=int)

        for member in current_week_joins:
            day_of_week = member.joined_at.date().weekday()
            current_week_counts[day_of_week] += 1

        for member in previous_week_joins:
            day_of_week = member.joined_at.date().weekday()
            previous_week_counts[day_of_week] += 1

        # Create the graph
        fig, ax = plt.subplots()
        ax.set_xlabel('Day of Week')
        ax.set_ylabel('Number of Joins')
        ax.set_ylim(0, max(max(previous_week_counts), max(current_week_counts)) + 5)
        xticks = np.array(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        x = np.arange(len(xticks))

        # Plot the data
        ax.plot(x, previous_week_counts, label='Previous Week', marker='o', markersize=8, linestyle='dashed')
        ax.plot(x, current_week_counts, label='Current Week', marker='o', markersize=8)

        # Set the x-axis ticks and tick labels
        ax.set_xticks(x)
        ax.set_xticklabels(xticks)

        # Add a legend to the graph
        ax.legend()

        # Save the graph as a PNG file
        plt.savefig('weekly_joins.png')

        # Create the embed
        embed = discord.Embed(title='Weekly Joins', color=0x2a2d31)
        embed.add_field(name='Previous Week', value=str(len(previous_week_joins)), inline=True)
        embed.add_field(name='Current Week', value=str(len(current_week_joins)), inline=True)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(
            text=f"{previous_week_start.strftime('%m/%d/%Y')} - {current_week_end.strftime('%m/%d/%Y')}"
        )

        # Add the graph as an image to the embed
        with open('weekly_joins.png', 'rb') as f:
            file = discord.File(f, filename='weekly_joins.png')
            embed.set_image(url='attachment://weekly_joins.png')

        # Send the embed to the channel
        await ctx.send(embed=embed, file=file)

        # Delete the PNG file
        plt.clf()
        plt.cla()
        plt.close()
        import os
        os.remove('weekly_joins.png')

async def setup(bot):
    await bot.add_cog(WeeklyJoins(bot))
