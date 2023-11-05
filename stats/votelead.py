import discord
from discord.ext import commands
import requests

class TopGGCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def votelead(self, ctx):
        """Displays the top 10 users and total votes from top.gg"""
        url = "https://top.gg/api/bots/733808027651801110/votes"
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjczMzgwODAyNzY1MTgwMTExMCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjgzMTk4MzM4fQ.CA7VhiS-3NXzg1yNPwH2E1LqtMxW7MO4cdHCwKeOhKA"} # Replace with your top.gg authorization token
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            votes = response.json()

            # Count votes per user using a dictionary
            vote_count = {}
            for vote in votes:
                user_id = vote["id"]
                if user_id not in vote_count:
                    vote_count[user_id] = {"username": vote["username"], "votes": 0}
                vote_count[user_id]["votes"] += 1

            # Sort the dictionary by votes and get the top 10
            sorted_votes = sorted(vote_count.values(), key=lambda x: x["votes"], reverse=True)[:10]

            leaderboard = [
                "`{num})` {name} - `{votes} votes` ".format(
                    num=index + 1, name=voter["username"], votes=voter["votes"]
                )
                for index, voter in enumerate(sorted_votes)
            ]
            total_votes = sum(v["votes"] for v in vote_count.values())
            embed = discord.Embed(title='Voting Leaderboard', description='\n'.join(leaderboard), color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("`Error retrieving data from top.gg`")

async def setup(bot):
    await bot.add_cog(TopGGCog(bot))
