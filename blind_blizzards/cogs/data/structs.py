import typing
from random import shuffle
from discord.ext import commands
import discord

OPTION_EMOJI = ["🇦", "🇧", "🇨", "🇩", "🇪"]
EMOJI_TO_INT = {emoji: index for index, emoji in enumerate(OPTION_EMOJI)}
# 5 options
MAGIC_EMBED_COLOUR = discord.Colour(0x36393E)
CANCEL_QUIZ = "❌"


def get_cancelled_embed(
    colour: typing.Union[discord.Colour, int] = MAGIC_EMBED_COLOUR
) -> discord.Embed:
    return discord.Embed(
        colour=colour,
        title="Cancelled Quiz",
        description=f"Ended the quiz prematurely.",
    )


def get_finished_embed(
    colour: typing.Union[discord.Colour, int] = MAGIC_EMBED_COLOUR
) -> discord.Embed:
    return discord.Embed(
        colour=colour, title="Finished Quiz", description=f"The quiz is over."
    )


def get_check(
    ctx: commands.Context, msg: discord.Message
) -> typing.Callable[[discord.Reaction, discord.User], bool]:
    """Generates the check for an option reaction on a message."""

    def check(reaction: discord.Reaction, user: discord.User):
        valid_emoji = reaction.emoji in OPTION_EMOJI + [CANCEL_QUIZ]
        valid_user = user == ctx.author
        valid_message = reaction.message == msg
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
        colour: typing.Union[discord.Colour, int] = MAGIC_EMBED_COLOUR,
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

        # for each option, add a field
        for emoji, option in zip(OPTION_EMOJI, options):
            embed.add_field(name=emoji, value=option)

        # tell the user what's going on
        embed.set_footer(
            text=f"React with your choice to answer, or with {CANCEL_QUIZ} to end:"
        )

        # return the embed and correct answer
        return embed, correct


class Quiz:
    """Structure used for holding multiple choice quizzes"""

    def __init__(
        self,
        title: str,
        questions: typing.List[QuizQuestion],
        colour: typing.Union[discord.Colour, int] = MAGIC_EMBED_COLOUR,
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
        msg: discord.Message = await ctx.send()
        # add option reactions
        for emoji in OPTION_EMOJI:
            await msg.add_reaction(emoji)
        # add cancel reaction
        await msg.add_reaction(CANCEL_QUIZ)

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
                text=f"{ctx.author.nick or ctx.author.name}'s score: {score}",
                embed=embed,
            )

            # wait for user response
            reaction, _ = await ctx.bot.wait_for("reaction_add", check=check)

            # if the user cancels
            if reaction.emoji == CANCEL_QUIZ:
                await msg.edit(embed=get_cancelled_embed(colour=self.colour))
                return

            # if they got the question right
            if EMOJI_TO_INT[reaction.emoji] == answer:
                score += 1

        # at the end of the quiz
        await msg.edit(
            text=f"Final score for {ctx.author.nick or ctx.author.name}: {score}",
            embed=get_finished_embed(colour=self.colour),
        )
