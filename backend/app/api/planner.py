from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.core.auth import (
    get_current_user_id
)

from app.models.vocabulary import (
    Vocabulary
)

from app.models.grammar_progress import (
    GrammarProgress
)

from app.models.grammar_topic import (
    GrammarTopic
)

from app.services.adaptive_plan_service import (
    AdaptivePlanService,
)

from app.services.adaptive_decision_service import (
    AdaptiveDecisionService,
)

router = APIRouter(
    prefix="/planner",
    tags=["Planner"],
)

adaptive_plan = (
    AdaptivePlanService()
)

decision_engine = (
    AdaptiveDecisionService()
)

@router.get("/today")
def today_plan(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    weak_words = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id
        )
        .order_by(
            Vocabulary.mastery_score.asc()
        )
        .limit(3)
        .all()
    )

    grammar_progress = (
        db.query(GrammarProgress)
        .filter(
            GrammarProgress.user_id
            == user_id
        )
        .all()
    )

    weakest_topic = None

    if grammar_progress:

        weakest = min(
            grammar_progress,
            key=lambda x:
            x.mastery_score
        )

        topic = (
            db.query(
                GrammarTopic
            )
            .filter(
                GrammarTopic.id
                == weakest.topic_id
            )
            .first()
        )

        weakest_topic = {
            "name":
            topic.title,

            "mastery":
            weakest.mastery_score,
        }

    return {

        "weak_words": [

            {
                "word":
                word.word,

                "mastery":
                word.mastery_score,
            }

            for word in weak_words
        ],

        "weak_topic":
        weakest_topic,

        "recommended_new_words":
        5,

        "recommended_flashcards":
        len(weak_words),

        "recommended_grammar":
        10,
    }

@router.get("/adaptive")
def adaptive_plan_today(

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    return adaptive_plan.build_plan(

        db=db,

        user_id=user_id,

    )

@router.get("/decision")
def learning_decision(

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    return decision_engine.next_learning_action(

        db=db,

        user_id=user_id,

    )