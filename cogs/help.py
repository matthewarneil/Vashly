from discord.ext import commands
import discord


class HelpView(discord.ui.View):
    def __init__(self, pages, current_page):
        super().__init__()
        self.pages = pages
        self.current_page = current_page

    async def show_page(self, page):
        self.current_page = page
        embed = self.pages[page]
        await self.message.edit(embed=embed, view=self)



    @discord.ui.button(label="◀️")
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            await self.show_page(self.current_page - 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(label="▶️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            await self.show_page(self.current_page + 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])  # This line is corrected


    async def error_handler(self, interaction: discord.Interaction, error: Exception):
        # Log the error
        print(f"An error occurred in the HelpView: {error}")

        # Send an error message to the user
        await interaction.response.send_message("`An error occurred while processing your request. Please try again later.`")


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help")
    async def help_command(self, ctx):
        """Displays this help message."""
        try:
            commands = [command for command in self.bot.commands if not command.hidden]
            pages = []
            num_commands = len(commands)
            for i in range(0, num_commands, 5):
                command_list = [
                    f"{command.help}\n```{command.name}```"
                    for command in commands[i:i + 5]
                ]
                help_embed = discord.Embed(title="Bot Commands", description="\n".join(command_list), color=0x2a2d31)
                help_embed.set_author(name="Vashly")
                help_embed.set_footer(text=f"Requested by {ctx.author.name}")
                help_embed.description = f"{help_embed.description}"
                help_embed.set_footer(text="View documentation for all commands.")
                help_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                pages.append(help_embed)

            current_page = 0
            view = HelpView(pages, current_page)
            view.message = await ctx.send(embed=pages[current_page], view=view)
        except Exception as e:
            # Log the error
            print(f"`An error occurred in the help command: {e}`")

            # Send an error message to the user
            await ctx.send("`An error occurred while processing your request. Please try again later.`")

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
