import typing
import discord
from discord.ext import commands

# general type
Number = typing.Union[int, float]

# cogs.help.cog
MaybeCog = typing.Optional[commands.Cog]
Commands = typing.List[commands.Command]
CommandsByCog = typing.Mapping[MaybeCog, Commands]

# cogs.help.paginator
CommandOrCog = typing.Union[commands.Cog, commands.Group, None]
CommandsAndCog = typing.Tuple[Commands, CommandOrCog]
PagesTyping = typing.List[typing.List[CommandsAndCog]]
