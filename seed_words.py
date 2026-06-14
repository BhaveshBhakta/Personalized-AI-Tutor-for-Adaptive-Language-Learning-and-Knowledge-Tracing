from app.db.database import SessionLocal
from app.models.german_word import GermanWord

db = SessionLocal()

words = [
    {
        "word": "Hund",
        "article": "der",
        "plural": "Hunde",
        "translation": "Dog",
        "category": "Animals",
        "frequency_rank": 100,
    },
    {
        "word": "Katze",
        "article": "die",
        "plural": "Katzen",
        "translation": "Cat",
        "category": "Animals",
        "frequency_rank": 120,
    },
    {
        "word": "Haus",
        "article": "das",
        "plural": "Häuser",
        "translation": "House",
        "category": "Home",
        "frequency_rank": 150,
    },
    {
        "word": "Buch",
        "article": "das",
        "plural": "Bücher",
        "translation": "Book",
        "category": "Education",
        "frequency_rank": 200,
    },
    {
        "word": "Wasser",
        "article": "das",
        "plural": "",
        "translation": "Water",
        "category": "Food",
        "frequency_rank": 90,
    },
]

for item in words:

    exists = (
        db.query(GermanWord)
        .filter(
            GermanWord.word
            == item["word"]
        )
        .first()
    )

    if not exists:
        db.add(
            GermanWord(**item)
        )

db.commit()

print("Seed completed")