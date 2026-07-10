from sqlalchemy.orm import Session

from app.models.learning_profile import (
    LearningProfile,
)

from app.models.flashcard import (
    Flashcard,
)

from app.models.grammar_progress import (
    GrammarProgress,
)


class LearnerContextService:


    def get_context(

        self,

        db: Session,

        user_id: int,

    ) -> dict:


        profile = (

            db.query(
                LearningProfile
            )

            .filter(

                LearningProfile.user_id
                == user_id

            )

            .first()

        )


        weak_flashcards = (

            db.query(
                Flashcard
            )

            .filter(

                Flashcard.user_id
                == user_id

            )

            .order_by(

                Flashcard.mastery_score.asc(),

                Flashcard.retrievability.asc(),

            )

            .limit(10)

            .all()

        )


        weak_grammar = (

            db.query(
                GrammarProgress
            )

            .filter(

                GrammarProgress.user_id
                == user_id,

                GrammarProgress.total_answers
                > 0,

            )

            .order_by(

                GrammarProgress.mastery_score.asc()

            )

            .limit(5)

            .all()

        )


        return {

            "profile": {

                "target_level": (

                    profile.target_level

                    if profile

                    else "A1"

                ),

                "daily_goal_minutes": (

                    profile.daily_goal_minutes

                    if profile

                    else 30

                ),

                "xp": (

                    profile.xp

                    if profile

                    else 0

                ),

                "streak": (

                    profile.streak

                    if profile

                    else 0

                ),

            },


            "weak_vocabulary": [

                {

                    "word":
                        flashcard.vocabulary.word,

                    "article":
                        flashcard.vocabulary.article,

                    "translation":
                        flashcard.vocabulary.translation,

                    "example_sentence":
                        flashcard.vocabulary.example_sentence,

                    "mastery_score":
                        flashcard.mastery_score,

                    "retrievability":
                        flashcard.retrievability,

                    "lapses":
                        flashcard.lapses,

                    "review_count":
                        flashcard.review_count,

                }

                for flashcard
                in weak_flashcards

                if flashcard.vocabulary
                is not None

            ],


            "weak_grammar": [

                {

                    "topic_id":
                        progress.topic_id,

                    "mastery_score":
                        progress.mastery_score,

                    "correct_answers":
                        progress.correct_answers,

                    "total_answers":
                        progress.total_answers,

                    "accuracy": (

                        round(

                            (
                                progress.correct_answers
                                /
                                progress.total_answers
                            )
                            * 100,

                            1,

                        )

                        if progress.total_answers
                        > 0

                        else 0

                    ),

                }

                for progress
                in weak_grammar

            ],

        }