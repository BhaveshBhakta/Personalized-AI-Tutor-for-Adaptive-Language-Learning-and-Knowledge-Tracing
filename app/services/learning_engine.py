from datetime import datetime
from datetime import timedelta

from app.models.flashcard import Flashcard
from app.models.learning_profile import LearningProfile


class LearningEngine:

    @staticmethod
    def review_flashcard(
        card: Flashcard,
        profile: LearningProfile,
        rating: str,
    ):

        now = datetime.utcnow()

        card.review_count += 1
        card.last_review = now

        if rating == "again":

            card.lapses += 1

            profile.xp += 1

            card.mastery_score = max(
                0,
                card.mastery_score - 10,
            )

            card.difficulty += 0.5

            card.stability *= 0.7

        elif rating == "hard":

            profile.xp += 3

            card.mastery_score = min(
                100,
                card.mastery_score + 2,
            )

            card.stability *= 1.2

        elif rating == "good":

            profile.xp += 5

            card.mastery_score = min(
                100,
                card.mastery_score + 5,
            )

            card.stability *= 1.6

        elif rating == "easy":

            profile.xp += 10

            card.mastery_score = min(
                100,
                card.mastery_score + 10,
            )

            card.stability *= 2

        card.retrievability = (
            card.mastery_score / 100
        )

        card.interval_days = max(
            1,
            int(card.stability),
        )

        card.next_review = (
            now
            + timedelta(
                days=card.interval_days
            )
        )