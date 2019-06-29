import typing
from random import shuffle
from discord.ext import commands
import discord
from math import floor
from .consts import (
    EMBED_THUMBNAIL,
    MAGIC_EMBED_COLOUR,
    AlignmentField,
    OPTION_EMOJI,
    EMOJI_TO_INT,
    CANCEL,
)
from lib.utils import value_map
from .typing import Colour, Emoji


def get_cancelled_embed(colour: Colour = MAGIC_EMBED_COLOUR) -> discord.Embed:
    embed = discord.Embed(
        colour=colour, title="Cancelled Quiz", description="Ended the quiz prematurely."
    )
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    return embed


def alignment_cancelled_embed(colour: Colour = MAGIC_EMBED_COLOUR) -> discord.Embed:
    embed = discord.Embed(
        colour=colour,
        title="Cancelled Alignment Test",
        description="Ended the test prematurely.\n*You'll never know...*",
    )
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    return embed


def game_cancelled_embed(colour: Colour = MAGIC_EMBED_COLOUR) -> discord.Embed:
    embed = discord.Embed(
        colour=colour,
        title="Ended Game",
        description="You quit before the end; the Earth is still in perilous waters.",
    )
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    return embed


def get_finished_embed(colour: Colour = MAGIC_EMBED_COLOUR) -> discord.Embed:
    embed = discord.Embed(
        colour=colour, title="Finished Quiz", description="The quiz is over."
    )
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    return embed


def get_alignment_embed(colour: Colour = MAGIC_EMBED_COLOUR) -> discord.Embed:
    embed = discord.Embed(
        colour=colour, title="Finished Alignment Test", description="The test is over."
    )
    embed.set_thumbnail(url=EMBED_THUMBNAIL)
    return embed


def get_check(
    ctx: commands.Context,
    msg: discord.Message,
    allowed_emoji: typing.List[Emoji] = None,
) -> typing.Callable[[discord.Reaction, discord.User], bool]:
    """Generates the check for an option reaction on a message."""
    if allowed_emoji is None:
        allowed_emoji = OPTION_EMOJI + [CANCEL]

    def check(reaction: discord.Reaction, user: discord.User):
        valid_emoji = reaction.emoji in allowed_emoji
        valid_user = user == ctx.author
        # for some reason these aren't equating properly
        valid_message = reaction.message.id == msg.id
        return all([valid_emoji, valid_user, valid_message])

    return check


class QuizQuestion:
    """Structure used for holding multiple-choice quiz questions"""

    def __init__(
        self,
        question_text: str,
        options: typing.Tuple[str, str, str, str, str],
        correct_option_index: int,
    ):
        self.text: str = question_text
        self.options: typing.Tuple[str, str, str, str, str] = options
        self.correct: int = correct_option_index

    async def prepare_question(
        self
    ) -> typing.Tuple[str, typing.Tuple[str, str, str, str, str], int]:
        """Called when generating a question during a quiz"""
        # copy self.options and add index items
        options = [[index, item] for index, item in enumerate(self.options)]

        # shuffle it the mathematically best number of times
        for _ in range(7):
            shuffle(options)

        # figure out which item is correct now
        correct = [
            index for index, item in enumerate(options) if item[0] == self.correct
        ][0]

        # strip the indexes from the options
        options = [item for index, item in options]

        # return the question, shuffled options, and correct answer
        return self.text, options, correct

    async def prepare_question_with_embed(
        self,
        quiz_name: str,
        question: int,
        max_question: int,
        colour: Colour = MAGIC_EMBED_COLOUR,
    ) -> typing.Tuple[discord.Embed, int]:
        """Called immediately before display during a quiz, for formatting.
        Quizzes can customise the colour of the embed using the `colour` parameter"""
        # get question data
        text, options, correct = await self.prepare_question()

        # make a basic embed, honouring the customisation settings
        embed = discord.Embed(
            colour=colour,
            title=f"{quiz_name} - question {question} of {max_question}",
            description=text,
        )
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        # for each option, add a field
        for emoji, option in zip(OPTION_EMOJI, options):
            embed.add_field(name=emoji, value=option)

        # tell the user what's going on
        embed.set_footer(
            text=f"React with your choice to answer, or with {CANCEL} to end:"
        )

        # return the embed and correct answer
        return embed, correct


class Quiz:
    """Structure used for holding multiple choice quizzes"""

    def __init__(
        self,
        title: str,
        questions: typing.List[QuizQuestion],
        colour: Colour = MAGIC_EMBED_COLOUR,
    ):
        self.title: str = title
        self.questions: typing.List[QuizQuestion] = questions
        self.colour = colour

    def add_questions(self, *questions: QuizQuestion):
        """Used to add additional questions after a Quiz has been created"""
        self.questions.extend(questions)

    async def do_quiz(self, ctx: commands.Context):
        """Run a quiz, including all Discord interaction"""
        # as we're not mutating the objects, there's no need for a deepcopy.
        # we *are* shuffling, though, hence the shallow copy.
        # we could, in theory, omit the copy and just shuffle it;
        # but that would cause problems if the same quiz is played under
        # multiple instances. </p>
        quiz_questions: typing.List[QuizQuestion] = self.questions.copy()

        # shuffle it the mathematically best number of times
        for _ in range(7):
            shuffle(quiz_questions)

        # set data for this run
        score = 0
        max_question = len(quiz_questions)
        # initialise the message
        msg: discord.Message = await ctx.send("Loading quiz...")
        # add option reactions
        for emoji in OPTION_EMOJI:
            await msg.add_reaction(emoji)
        # add cancel reaction
        await msg.add_reaction(CANCEL)

        # get check now to avoid redefining each loop
        check = get_check(ctx, msg)

        # main quiz loop
        for number, question in enumerate(quiz_questions, 1):
            # retrieve the question data
            embed, answer = await question.prepare_question_with_embed(
                self.title, number, max_question, self.colour
            )

            # ask the question
            await msg.edit(
                content=f"{ctx.author.nick or ctx.author.name}'s score: {score}",
                embed=embed,
            )

            # wait for user response
            reaction, _ = await ctx.bot.wait_for("reaction_add", check=check)

            # if the user cancels
            if reaction.emoji == CANCEL:
                await msg.edit(embed=get_cancelled_embed(colour=self.colour))
                return

            # if they got the question right
            if EMOJI_TO_INT[reaction.emoji] == answer:
                score += 1

        # at the end of the quiz
        await msg.edit(
            content=f"Final score for {ctx.author.nick or ctx.author.name}: {score}",
            embed=get_finished_embed(colour=self.colour),
        )


class AlignmentQuestion:
    """Structure used for holding multiple-choice alignment test questions"""

    def __init__(
        self,
        question_text: str,
        options: typing.Tuple[
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
        ],
    ):
        self.text: str = question_text
        self.options: typing.Tuple[
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
        ] = options

    async def prepare_question(
        self
    ) -> typing.Tuple[
        str,
        typing.Tuple[
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
            typing.Tuple[str, AlignmentField, int],
        ],
    ]:
        """Called when generating a question during an alignment test"""
        # copy self.options
        options = self.options.copy()
        # shuffle it the mathematically best number of times
        for _ in range(7):
            shuffle(options)
        # return the question and shuffled options
        return self.text, options

    async def prepare_question_with_embed(
        self, colour: Colour = MAGIC_EMBED_COLOUR
    ) -> typing.Tuple[discord.Embed, int]:
        """Called immediately before display during a quiz, for formatting.
        Quizzes can customise the colour of the embed using the `colour` parameter"""
        # get question data
        text, options = await self.prepare_question()

        # make a basic embed, honouring the customisation settings
        embed = discord.Embed(colour=colour, description=text)
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        # for each option, add a field
        for emoji, option in zip(OPTION_EMOJI, options):
            embed.add_field(name=emoji, value=option[0])

        # tell the user what's going on
        embed.set_footer(
            text=f"React with your choice to answer, or with {CANCEL} to end:"
        )

        # return the embed and alignment data
        return embed, [option[1:] for option in options]


class AlignmentTest:
    """Structure used for holding multiple choice alignment tests"""

    def __init__(
        self,
        title: str,
        questions: typing.List[AlignmentQuestion],
        alignment_table: typing.Tuple[
            typing.Tuple[str, str, str],
            typing.Tuple[str, str, str],
            typing.Tuple[str, str, str],
        ],
        # This should be symmetric i.e. all scores within 0 ± max_x_displacement
        max_x_displacement: int,
        # This should be symmetric i.e. all scores within 0 ± max_y_displacement
        max_y_displacement: int,
        colour: Colour = MAGIC_EMBED_COLOUR,
        as_images: bool = False,
    ):
        self.title: str = title
        self.questions: typing.List[AlignmentQuestion] = questions
        self.alignment_table = alignment_table
        self.x = max_x_displacement
        self.y = max_y_displacement
        self.colour = colour
        self.images = as_images

    def add_questions(self, *questions: AlignmentQuestion):
        """Used to add additional questions after an AlignmentTest has been created"""
        self.questions.extend(questions)

    async def do_test(self, ctx: commands.Context):
        """Run an alignment test, including all Discord interaction"""
        # as we're not mutating the objects, there's no need for a deepcopy.
        # we *are* shuffling, though, hence the shallow copy.
        # we could, in theory, omit the copy and just shuffle it;
        # but that would cause problems if the same quiz is played under
        # multiple instances. </p>
        quiz_questions: typing.List[AlignmentQuestion] = self.questions.copy()

        # shuffle it the mathematically best number of times
        for _ in range(7):
            shuffle(quiz_questions)

        # set data for this run
        x = y = 0
        max_question = len(quiz_questions)
        # initialise the message
        msg: discord.Message = await ctx.send("Loading alignment test...")
        # add option reactions
        for emoji in OPTION_EMOJI:
            await msg.add_reaction(emoji)
        # add cancel reaction
        await msg.add_reaction(CANCEL)

        # get check now to avoid redefining each loop
        check = get_check(ctx, msg)

        # main quiz loop
        for number, question in enumerate(quiz_questions, 1):
            # retrieve the question data
            embed, answer_key = await question.prepare_question_with_embed(self.colour)

            # ask the question
            await msg.edit(
                content=f"[{self.title}] Question {number} of {max_question}",
                embed=embed,
            )

            # wait for user response
            reaction, _ = await ctx.bot.wait_for("reaction_add", check=check)

            # if the user cancels
            if reaction.emoji == CANCEL:
                await msg.edit(embed=alignment_cancelled_embed(colour=self.colour))
                return

            # get the chosen answer in [field, increment] form
            # some increments will be negative, indicated a downward shift
            # in that alignment
            answer = answer_key[EMOJI_TO_INT[reaction.emoji]]
            if answer[0] == AlignmentField.X:
                x += answer[1]
            elif answer[0] == AlignmentField.Y:
                y += answer[1]

        # at the end of the quiz
        alignment = self.alignment_table[
            floor(value_map(y, -self.y, self.y + 1, 0, 3))
        ][floor(value_map(x, -self.x, self.x + 1, 0, 3))]
        user = ctx.author.nick or ctx.author.name
        if not self.images:
            await msg.edit(
                content=f"Alignment for {user}: {alignment}",
                embed=get_alignment_embed(colour=self.colour),
            )
        else:
            embed = discord.Embed(colour=self.colour)
            embed.set_thumbnail(url=EMBED_THUMBNAIL)
            embed.set_image(url=alignment)
            await msg.edit(content=f"Alignment for {user}:", embed=embed)


class GameNode:
    def __init__(
        self,
        short_text: str,
        long_text: str,
        children: typing.List[GameNode],
        colour: Colour = MAGIC_EMBED_COLOUR,
    ):
        self.as_option = short_text
        self.text = long_text
        self.children = children
        self.colour = colour

    def to_embed(self, shuffled_children):
        """Returns the embed for this node"""
        # make the embed object
        embed = discord.Embed(colour=self.colour, description=self.text)

        # add fields for each child
        for emoji, child in zip(OPTION_EMOJI, shuffled_children):
            embed.add_field(name=emoji, value=child.as_option)

        # set standard embed data - thumbnail and footer
        embed.set_thumbnail(url=EMBED_THUMBNAIL)
        embed.set_footer(text=f"Select your choice below, or quit with {CANCEL}:")

        # send back the embed
        return embed

    async def get_next_node(self):
        """Performs the Discord logic of retrieving the next node"""
        # generate the check for the node's response

        # the little zip hack shortens the list of emoji so that it is the same
        # length as our list of children
        # N.B. there might be a better way of doing this
        check = get_check(
            self.ctx,
            self.message,
            [emoji for emoji, child in zip(OPTION_EMOJI, self.children)] + [CANCEL],
        )

        # copy our children
        shuffled_children = self.children.copy()

        # shuffle them the mathematically best number of times
        for _ in range(7):
            shuffle(shuffled_children)

        # edit the message with our embed
        await self.message.edit(embed=self.to_embed(shuffled_children))

        # wait for user response
        reaction, _ = await self.ctx.bot.wait_for("reaction_add", check=check)

        # if the user cancels
        if reaction.emoji == CANCEL:
            await self.message.edit(embed=game_cancelled_embed(colour=self.colour))
            # tell the node we don't want to continue
            return -1

        # tell the node which option we picked
        return EMOJI_TO_INT[reaction.emoji]

    async def run_this_node(
        self,
        ctx: commands.Context = None,
        message: discord.Message = None,
        is_first: bool = False,
    ):
        """Run the node, playing the rest of the game"""
        # initialise self.ctx from ctx and self.message from message
        # N.B. if this node is first then message is None
        self.ctx = ctx
        self.message = message

        # if this is the first node, initialise the discord data:
        if is_first:
            # send our message, with dummy text for now
            self.message = await ctx.send("Loading game...")

            # add our reactions
            for emoji in OPTION_EMOJI + [CANCEL]:
                await self.message.add_reaction(emoji)

            # we've finished setup (reacting takes a while), so
            # clear the dummy text with a zero width space
            await self.message.edit(content="\u200b")

        # get the next node
        next_node = await self.get_next_node()

        # user cancelled
        if next_node == -1:
            return

        # get next node
        child = self.children[next_node]
        # run it
        await child.run_this_node(ctx, message)


class EndNode(GameNode):
    def __init__(
        self,
        short_text: str,
        long_text: str,
        children: typing.List[GameNode],
        colour: Colour = MAGIC_EMBED_COLOUR,
        long_text_is_image: bool = False,
    ):
        self.as_option = short_text
        self.text = long_text
        self.is_image = long_text_is_image
        self.children = children
        self.colour = colour

    async def run_this_node(self, ctx: commands.Context, message: discord.Message):
        """As this is the last node, all that is left is to show the embed."""
        # generate embed
        if not self.is_image:
            # it's not an image, generate in one statement
            embed = discord.Embed(
                colour=self.colour, description=self.text, title="The game is now over"
            )
        else:
            # it's an image, need two statements
            embed = discord.Embed(colour=self.colour, title="The game is now over")
            embed.set_image(url=self.text)

        # set standard embed data - thumbnail
        embed.set_thumbnail(url=EMBED_THUMBNAIL)

        # edit onto the message
        await message.edit(embed=embed)
