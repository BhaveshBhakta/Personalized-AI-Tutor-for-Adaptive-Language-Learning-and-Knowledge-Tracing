from app.db.database import SessionLocal

from app.models.grammar_question import (
    GrammarQuestion
)

db = SessionLocal()

questions = [

    {
        "topic_id": 1,
        "question":
        "_____ Hund",

        "option_a":
        "der",

        "option_b":
        "die",

        "option_c":
        "das",

        "correct_answer":
        "der",
    },

    {
        "topic_id": 1,
        "question":
        "_____ Katze",

        "option_a":
        "der",

        "option_b":
        "die",

        "option_c":
        "das",

        "correct_answer":
        "die",
    },

    {
        "topic_id": 1,
        "question":
        "_____ Haus",

        "option_a":
        "der",

        "option_b":
        "die",

        "option_c":
        "das",

        "correct_answer":
        "das",
    },

]

for item in questions:

    exists = (
        db.query(
            GrammarQuestion
        )
        .filter(
            GrammarQuestion.question
            == item["question"]
        )
        .first()
    )

    if not exists:

        db.add(
            GrammarQuestion(**item)
        )

db.commit()

print("Seeded")