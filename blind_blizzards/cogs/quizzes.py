# -*- coding: utf-8 -*-

# interaction with discord
from discord.ext import commands
import discord

# quiz data
from .data import quizzes

# reload quiz data
from importlib import reload

# determining the user's selection
from fuzzywuzzy import process

# if they didn't select
import random

# for creating admin-only commands
from lib.checks import _check


class Quizzes(commands.Cog):
    """The cog that handles quizzes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # a list of quiz titles to their quizzes
        self.quizzes_by_name = {quiz.title: quiz for quiz in quizzes.quizzes}

    @commands.command()
    @_check()
    async def reload_quizzes(self, ctx: commands.Context):
        """Reloads the list of available quizzes"""
        # reload cogs.data.quizzes
        reload(quizzes)
        # construct quizzes_by_name again
        self.quizzes_by_name = {quiz.title: quiz for quiz in quizzes.quizzes}
        # send back a nice little message
        await ctx.send(f"Reloaded {len(self.quizzes_by_name)} quizzes")

    @commands.command(aliases=["takequiz", "quiz"])
    async def take_quiz(self, ctx: commands.Context, *, quiz_name: str = None):
        """Take a quiz. If none specified, one will be chosen at random"""
        # if no quiz specified, pick a random one
        if not quiz_name:
            # random.choice doesn't like dict_keys
            quiz_name = random.choice([i for i in self.quizzes_by_name])

        # find the closest match, no matter what it is and strip the accuracy
        quiz_name = process.extractOne(quiz_name, self.quizzes_by_name.keys())[0]

        # get the object from the name
        quiz = self.quizzes_by_name[quiz_name]

        # do the quiz using Quiz.do_quiz
        await quiz.do_quiz(ctx)

    @commands.command(aliases=["quizzes", "list", "listquizzes"])
    async def list_quizzes(self, ctx: commands.Context):
        """Shows the list of quizzes"""
        # get the quizzes in a newline-separated format
        quizzes = "\n".join(self.quizzes_by_name.keys())
        # TODO: paginate
        await ctx.send(quizzes)


def setup(bot: commands.Bot):
    bot.add_cog(Quizzes(bot))
