from app.db.database import SessionLocal
from app.models.grammar_topic import GrammarTopic

db = SessionLocal()

topics = [
    {
        "title": "Articles",
        "level": "A1",
        "explanation":
        "German nouns use der, die or das."
    },
    {
        "title": "Plural Forms",
        "level": "A1",
        "explanation":
        "German nouns have plural forms."
    },
    {
        "title": "Verb Conjugation",
        "level": "A1",
        "explanation":
        "Verbs change according to subject."
    },
    {
        "title": "Sentence Structure",
        "level": "A1",
        "explanation":
        "German sentences follow strict word order."
    },
]

for item in topics:

    exists = (
        db.query(GrammarTopic)
        .filter(
            GrammarTopic.title
            == item["title"]
        )
        .first()
    )

    if not exists:
        db.add(
            GrammarTopic(**item)
        )

db.commit()

print("Grammar topics seeded")