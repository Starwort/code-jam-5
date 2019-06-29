import typing

from discord.ext import commands

import config

from .paginator import BotOrCogHelp, GroupHelp, CommandHelp


per_page = getattr(config, "COMMANDS_PER_HELP_PAGE", 10)


class HelpCommand(commands.HelpCommand):
    """The customized help command"""

    def __init__(self):
        super().__init__(command_attrs={"help": "help.help.help_help"})

    async def send_command_help(self, command: commands.Command):
        """The coroutine to run when requested help for a single command.
        
        Parameters
        ----------
        command: discord.ext.commands.Command
            The command requested
        
        """

        paginator = CommandHelp(self, self.context.bot, self.context, command)

        await paginator.paginate()

    async def send_group_help(self, group: commands.Group):
        """THe coroutine to run when requested help for a Group (a command with subcommands).
        
        Parameters
        ----------
        group: discord.ext.commands.Group
            The group requested
        """

        cmds = group.commands

        # filter commands for the ones that pass all checks
        cmds = await self.filter_commands(cmds, sort=True)

        pages = []
        current_page = []
        if len(cmds) > per_page:

            # splits the group into multiple pages
            for i in range(0, len(cmds), per_page):
                end_index = i + per_page
                current_page.append((group, cmds[i:end_index]))
                pages.append(current_page)
                current_page = []

        else:
            current_page.append((group, cmds))
            pages.append(current_page)
        paginator = GroupHelp(self, self.context.bot, self.context, pages)

        await paginator.paginate()

    async def send_cog_help(self, cog: commands.Cog):
        """The coroutine to run when requested help for a Cog
        
        Parameters
        ----------
        cog: discord.ext.commands.Cog
            The cog requested
        """

        cmds = cog.get_commands()

        # filter commands for the ones that pass all checks
        cmds = await self.filter_commands(cmds, sort=True)

        pages = []
        current_page = []
        if len(cmds) > per_page:

            # splits the cog into multiple pages
            for i in range(0, len(cmds), per_page):
                end_index = i + per_page
                current_page.append((cog, cmds[i:end_index]))
                pages.append(current_page)

        else:
            current_page.append((cog, cmds))
            pages.append(current_page)

        paginator = BotOrCogHelp(self, self.context.bot, self.context, pages)

        await paginator.paginate()

    async def send_bot_help(
        self,
        mapping: typing.Mapping[
            typing.Optional[commands.Cog], typing.List[commands.Command]
        ],
    ):
        """The coroutine to run when requested generic helo for the entire bot

        Parameters
        ----------
        mapping: Mapping[Optional[discord.ext.commands.Cog], List[discord.ext.commands.Command]]
            The mapping of each Cog to a list of their commands. Commands not in a cog are grouped
            together with the key being `None`
        """

        # filter commands
        mapping = {
            cog: await self.filter_commands(cmds, sort=True)
            for cog, cmds in mapping.items()
        }

        # sort cogs by number of commands
        keys = sorted(
            mapping.keys(),
            key=lambda cog: len(cog.get_commands()) if cog else 0,
            reverse=True,
        )
        pages = []
        current_page = []
        cmds_on_current_pg = 0
        for cog in keys:
            cmds = mapping[cog]

            # if all commands failed check, ignore cog
            if not cmds:
                continue

            if len(cmds) > per_page:
                # split into multiple pages
                if current_page:
                    pages.append(current_page)
                    cmds_on_current_pg = 0
                    current_page = []

                for i in range(0, len(cmds), per_page):
                    end_index = i + per_page
                    current_page.append((cog, cmds[i:end_index]))
                    if len(cmds[i:end_index]) == per_page:
                        pages.append(current_page)
                        current_page = []

                if current_page:
                    cmds_on_current_pg = len(current_page[0][1])

            # check if there's not enough space on current page
            elif len(cmds) > per_page - cmds_on_current_pg:
                pages.append(current_page)
                cmds_on_current_pg = 0
                current_page = []
                current_page.append((cog, cmds))
                cmds_on_current_pg = len(cmds)
            else:
                current_page.append((cog, cmds))
                cmds_on_current_pg += len(cmds)

        # add the last page if it isn't empty
        if current_page:
            pages.append(current_page)

        paginator = BotOrCogHelp(self, self.context.bot, self.context, pages)

        await paginator.paginate()
