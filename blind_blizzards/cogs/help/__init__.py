from discord.ext import commands

from .cog import Help


def setup(bot: commands.Bot):
    """Cog load."""

    bot.add_cog(Help(bot))
