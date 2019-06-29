import asyncio
import discord
import typing
from discord.ext import commands

PagesTyping = typing.List[
    typing.List[
        typing.Tuple[
            typing.Union[commands.Cog, commands.Group, None],
            typing.List[commands.Command],
        ]
    ]
]


class HelpPaginator:
    """The paginator for help.

    Parameters
    ----------
    help_command: discord.ext.commands.HelpCommand
        The help_command that invoked this paginator.
    bot: discord.ext.commands.Bot
        The discord bot currently running
    ctx: discord.ext.commands.Context
        The current context of the Discord message
    pages: PagesTyping (see above)
        The pages to add to the paginator

    Attributes
    ----------
    author: discord.BaseUser
        A shortcut for `self.context.author` - The invoker of the help command
    channel: typing.Union[discord.TextChannel, discord.DMChannel]
        A shortcut for `self.context.channel` - The channel in which the command was invoked
    original_message: discord.Mesage
        A shortcut for `self.context.message` - The message that invoked the command
    prefix: str
        The cleaned up invoke prefix of the help command
    embed: discord.Embed
        The embed that is frequently edited to send to discord
    reaction_emoji: typing.List[typing.Tuple[str, typing.Callable]]
        The list of possible emoji to react to and their function
    maximum_pages: int
        The number of pages
    paginating: bool
        Whether we are paginating or not
    total: int
        The total number of commands in the paginator
    current_page: typing.Optional[int]
        The index of the current page being displayed
    match: typing.Optional[typing.Callable]
        The method assigned to the reacted emoji. Altered in the predicate
    help_message: typing.Optional[discord.Message]
        The message containing the bot's reply to the help invoke
    """

    def __init__(
        self,
        help_command: commands.HelpCommand,
        bot: commands.Bot,
        ctx: commands.Context,
        pages: PagesTyping,
    ):
        self.help_command: commands.HelpCommand = help_command
        self.bot: commands.Bot = bot
        self.context: commands.Context = ctx
        self.author: discord.BaseUser = ctx.author
        self.channel: typing.Union[discord.TextChannel, discord.DMChannel] = ctx.channel
        self.original_message: discord.Message = ctx.message

        self.pages: PagesTyping = pages
        self.prefix: str = help_command.clean_prefix

        self.embed: discord.Embed = discord.Embed(colour=0x36393E)
        self.reaction_emoji: typing.List[typing.Tuple[str, typing.Callable]] = [
            (
                "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
                self.first_page,
            ),
            ("\N{BLACK LEFT-POINTING TRIANGLE}", self.previous_page),
            ("\N{BLACK RIGHT-POINTING TRIANGLE}", self.next_page),
            (
                "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
                self.last_page,
            ),
            ("\N{BLACK SQUARE FOR STOP}", self.stop_pages),
        ]

        self.maximum_pages: int = len(pages)
        self.paginating: bool = len(pages) != 1

        self.total: int = 0
        for page in pages:
            for section in page:
                _cog, cmds = section
                self.total += len(cmds)

        self.current_page: typing.Optional[int] = None
        self.match: typing.Optional[typing.Callable]
        self.help_message: typing.Optional[discord.Message] = None

    def predicate(self, reaction: discord.Reaction, user: discord.BaseUser):
        """The check for a reaction_add"""

        if user.id != self.author.id:
            return False

        if reaction.message.id != self.help_message.id:
            return

        for (emoji, func) in self.reaction_emoji:
            if reaction.emoji == emoji:
                self.match = func
                return True
        return False

    async def prepare_embed(self, page: int) -> typing.NoReturn:
        """The function called to prepare the embed before it is send/edited.

        This is overwritten when subclassed.

        Parameters
        ----------
        page: int
            The index of the current page to prepare
        """

        raise NotImplementedError

    async def show(self, page: int, *, first: bool = False) -> None:
        """Displays the given page in discord

        Parameters
        ----------
        page: int
            The index of the current page to show

        first: bool (default False)
            Whether this is the first time this is being called and hence
            the return message hasn't been sent yet.
        """

        self.current_page = page
        await self.prepare_embed(page)

        if not self.paginating:
            await self.channel.send(embed=self.embed)
            return

        if not first:
            await self.help_message.edit(embed=self.embed)
            return

        self.help_message = await self.channel.send(embed=self.embed)
        for reaction, _func in self.reaction_emoji:
            if self.maximum_pages == 2 and reaction in ("\u23ed", "\u23ee"):
                # Don't add first and last page when there are only two
                continue
            await self.help_message.add_reaction(reaction)

    async def first_page(self):
        """When the Double Left Triangle is clicked."""

        await self.show(0)

    async def last_page(self):
        """When the Double Right Triangle is clicked."""

        await self.show(self.maximum_pages - 1)

    async def next_page(self):
        """WHen the Single Right Triangle is clicked."""

        new = self.current_page + 1
        # check limits
        if new < self.maximum_pages:
            await self.show(new)

    async def previous_page(self):
        """When the Single Left Triangle is clicked."""

        new = self.current_page - 1
        # check limits
        if new < self.maximum_pages:
            await self.show(new)

    async def stop_pages(self):
        """When the Stop button is clicked."""

        await self.help_message.edit(
            content=await self.translate("help.quit"), embed=None
        )  # remove embed after pagination
        try:
            await self.help_message.clear_reactions()
        except discord.errors.DiscordException:
            for emoji, _func in self.reaction_emoji:
                await self.help_message.remove_reaction(emoji, self.context.me)
        self.paginating = False

    async def paginate(self) -> None:
        """The commnand to esentially start the paginator."""

        first_page = self.show(0, first=True)
        if not self.paginating:
            await first_page
            return

        # If paginating, allows us to react straight away
        self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=self.predicate, timeout=120.0
                )

            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.stop_pages()
                except discord.DiscordException:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(reaction, user)
            except discord.DiscordException:
                # leave it if we can't remove it
                pass

            # self.match updates to the correct method during the predicate
            await self.match()
