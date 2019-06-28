from structs import Quiz, QuizQuestion

example_quiz = Quiz("An example quiz to demonstrate how they work", [])

example_quiz.add_questions(
    [
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
    ]
)
