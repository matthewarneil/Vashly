import discord
import random
import locale
from discord.ext import commands

class ProfitCalc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Set the locale to the user's default locale
        locale.setlocale(locale.LC_ALL, '')

    @commands.hybrid_command()
    async def profitcal(self, ctx, symbol: str = None, purchase_price: float = None, quantity: float = None, current_price: float = None):
        """Calculates the profit/loss of a cryptocurrency investment.
        
        Parameters
        -----------
        symbol: symbol
            Enter crypto symbol.

        purchase_price: purchase_price
            Enter price you bought crypto at.

        quantity: quantity
            Enter the amount you bought.

        current_price: current_price
            Enter current price of coin.
        
        """
        if symbol is None or purchase_price is None or quantity is None or current_price is None:
            embed = discord.Embed(title="Error", description="Please provide a cryptocurrency symbol, purchase price, quantity, and current price.", color=0x2a2d31)
            await ctx.send(embed=embed)
            return

        if not symbol.isalnum() or len(symbol) > 10:
            embed = discord.Embed(title="Error", description="Invalid cryptocurrency symbol. Please enter a valid symbol (alphanumeric and <= 10 characters).", color=0x2a2d31)
            await ctx.send(embed=embed)
            return

        profit = (current_price - purchase_price) * quantity

        embed = discord.Embed(title='Profit Calculator', description='Please note that this calculator provides an estimate of your cryptocurrency investment\'s profit/loss and does not factor in trading fees or tax implications. As such, it should not be used as an exact calculation of your profit/loss.', color=0x2a2d31)
        embed.add_field(name='Symbol', value=f'```{symbol.upper()}```', inline=False)
        embed.add_field(name='Purchase Price', value=f'```${purchase_price:,.2f}```', inline=False)
        embed.add_field(name='Quantity', value=f'```{quantity:,.8f}```', inline=False)
        embed.add_field(name='Current Price', value=f'```${current_price:,.2f}```', inline=False)
        embed.add_field(name='Profit/Loss', value=f'```${profit:,.2f}```', inline=False)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        # Send the embed
        await ctx.send(embed=embed)

async def setup(bot):
   await bot.add_cog(ProfitCalc(bot))
