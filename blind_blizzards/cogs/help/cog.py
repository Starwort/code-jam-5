from discord.ext import commands

from .help import CustomHelpCommand


class Help(commands.Cog):
    """The cog containing the help command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command = CustomHelpCommand()
        self.bot.help_command.cog = self

    def cog_unload(self):
        """When the cog is unloaded."""

        # set back to default
        self.bot.help_command = commands.HelpCommand()
