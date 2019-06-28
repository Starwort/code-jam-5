from .structs import (
    Quiz,
    QuizQuestion,
    AlignmentTest,
    AlignmentQuestion,
    AlignmentField,
)


quizzes = []
tests = []


example_quiz = Quiz("An example quiz to demonstrate how they work", [])
example_quiz.add_questions(
    QuizQuestion(
        "Example question\nThis isn't guaranteed to be first.",
        [
            "wrong answer #1",
            "wrong answer #2",
            "correct answer",
            "wrong answer #3",
            "answers get shuffled too",
        ],
        2,
    ),
    QuizQuestion(
        "Another example question\nQuestions get shuffled before being used",
        [
            "So don't use question numbers",
            "Or incremental question types.",
            "Don't make sentences like I am here",
            "Because they'll be out of order",
            "Correct answer",
        ],
        4,
    ),
    QuizQuestion(
        "How many options go in each question?",
        [
            "It's always the same",
            "There are 5 options in each question",
            "But only one is correct",
            "It's not this one",
            "Or this one",
        ],
        1,
    ),
)

# if we wanted this to be a real quiz
# we'd uncomment this line:
quizzes.append(example_quiz)

example_test = AlignmentTest(
    "Example Alignment Test",
    [],
    [
        ["Top left", "Top middle", "Top right"],
        ["Middle left", "Middle middle", "Middle right"],
        ["Bottom left", "Bottom middle", "Bottom right"],
    ],
    24,
    24,
)
example_test.add_questions(
    AlignmentQuestion(
        "When you answer this question, your X value will:",
        [
            ["Increase by 8", AlignmentField.X, 8],
            ["Increase by 4", AlignmentField.X, 4],
            # third value can really be anything you like here
            ["Not change", AlignmentField.NONE, 0],
            ["Decrease by 4", AlignmentField.X, -4],
            ["Decrease by 8", AlignmentField.X, -8],
        ],
    ),
    AlignmentQuestion(
        # don't do this actually
        # you can but don't
        "You can mix field types (but keep them symmetric)",
        [
            ["X += 8", AlignmentField.X, 8],
            ["Y -= 4", AlignmentField.Y, -4],
            ["`pass`", AlignmentField.NONE, 0],
            ["Y += 4", AlignmentField.Y, 4],
            ["X -= 8", AlignmentField.X, -8],
        ],
    ),
    AlignmentQuestion(
        "Try to get max displacement to a multiple of 3",
        [
            ["X += 8", AlignmentField.X, 8],
            ["Y -= 20", AlignmentField.Y, -20],
            ["And put that in the two displacement fields", AlignmentField.NONE, 0],
            ["Y += 20", AlignmentField.Y, 20],
            ["X -= 8", AlignmentField.X, -8],
        ],
    ),
)

# another fake test
tests.append(example_test)
