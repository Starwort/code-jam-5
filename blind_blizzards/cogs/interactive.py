# -*- coding: utf-8 -*-

# interaction with discord
from discord.ext import commands
import discord

# quiz data
from data import interactive

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
        # a list of quiz/test titles to their quizzes/tests
        self.quizzes_by_name = {quiz.title: quiz for quiz in interactive.quizzes}
        self.tests_by_name = {test.title: test for test in interactive.tests}

    @commands.command()
    @_check()
    async def reload_quizzes(self, ctx: commands.Context):
        """Reloads the list of available quizzes"""
        # reload cogs.data.quizzes
        reload(interactive)
        # construct quizzes_by_name/tests_by_name again
        self.quizzes_by_name = {quiz.title: quiz for quiz in interactive.quizzes}
        self.tests_by_name = {test.title: test for test in interactive.tests}
        # send back a nice little message
        await ctx.send(
            f"Reloaded {len(self.quizzes_by_name)} quizzes and {len(self.tests_by_name)} tests"
        )

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

    @commands.command(aliases=["quizzes", "listquizzes"])
    async def list_quizzes(self, ctx: commands.Context):
        """Shows the list of quizzes"""
        # get the quizzes in a newline-separated format
        quizzes = "\n".join(self.quizzes_by_name.keys())
        # TODO: paginate
        await ctx.send(quizzes)

    @commands.command(aliases=["taketest", "test"])
    async def take_test(self, ctx: commands.Context, *, test_name: str = None):
        """Take a test. If none specified, one will be chosen at random"""
        # if no test specified, pick a random one
        if not test_name:
            # random.choice doesn't like dict_keys
            test_name = random.choice([i for i in self.tests_by_name])

        # find the closest match, no matter what it is and strip the accuracy
        test_name = process.extractOne(test_name, self.tests_by_name.keys())[0]

        # get the object from the name
        test = self.tests_by_name[test_name]

        # do the test using AlignmentTest.do_test
        await test.do_test(ctx)

    @commands.command(aliases=["tests", "listtests"])
    async def list_tests(self, ctx: commands.Context):
        """Shows the list of tests"""
        # get the tests in a newline-separated format
        tests = "\n".join(self.tests_by_name.keys())
        # TODO: paginate
        await ctx.send(tests)


def setup(bot: commands.Bot):
    bot.add_cog(Quizzes(bot))
