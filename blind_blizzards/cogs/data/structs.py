import typing
from random import shuffle

OPTION_EMOJI = ["🇦", "🇧", "🇨", "🇩"]


class QuizQuestion:
    """Structure used for holding multiple-choice quiz questions"""

    def __init__(
        self,
        question_text: str,
        options: typing.List[str],
        correct_option_index: int
    ):
        self.text: str = question_text
        self.options: typing.List[str] = options
        self.correct: int = correct_option_index

    async def prepare_question(self) -> typing.Tuple[str, typing.List[str], int]:
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


class Quiz:
    """Structure used for holding multiple choice quizzes"""

    def __init__(self, title: str, questions: typing.List[QuizQuestion]):
        self.title: str = title
        self.questions: typing.List[QuizQuestion] = questions

    def add_questions(self, *questions: QuizQuestion):
        self.questions.extend(questions)
