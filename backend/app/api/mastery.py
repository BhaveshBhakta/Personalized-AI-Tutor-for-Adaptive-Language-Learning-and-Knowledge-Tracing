from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.auth import (
    get_current_user_id,
)

from app.db.dependencies import (
    get_db,
)

from app.models.topic_mastery import (
    TopicMastery,
)

from app.services.knowledge_tracing_service import (
    KnowledgeTracingService,
)

from app.models.adaptive_exercise import (
    AdaptiveExercise,
)

from app.models.learning_signal import (
    LearningSignal,
)

from app.services.skill_seed_service import (
    SkillSeedService,
)

router = APIRouter(
    prefix="/mastery",
    tags=["Mastery"],
)


knowledge_tracer = (
    KnowledgeTracingService()
)

skill_seed_service = (
    SkillSeedService()
)

@router.post("/recalculate")
def recalculate_mastery(

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    exercise_topics = (

        db.query(

            AdaptiveExercise.category,

            AdaptiveExercise.topic,

        )

        .filter(

            AdaptiveExercise.user_id
            == user_id

        )

        .distinct()

        .all()

    )


    signal_topics = (

        db.query(

            LearningSignal.category,

            LearningSignal.topic,

        )

        .filter(

            LearningSignal.user_id
            == user_id

        )

        .distinct()

        .all()

    )


    topic_pairs = set(

        exercise_topics
        + signal_topics

    )


    updated = []


    for category, topic in topic_pairs:


        result = (

            knowledge_tracer
            .calculate_topic_mastery(

                db=db,

                user_id=user_id,

                category=category,
                topic=topic,

            )

        )


        updated.append({

            "category":
                result.category,

            "topic":
                result.topic,

            "mastery_probability":
                result.mastery_probability,

            "confidence":
                result.confidence,

            "evidence_count":
                result.evidence_count,

        })


    return {

        "updated_count":
            len(updated),

        "topics":
            updated,

    }


@router.get("/topics")
def list_topic_mastery(

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    topics = (

        db.query(
            TopicMastery
        )

        .filter(

            TopicMastery.user_id
            == user_id

        )

        .order_by(

            TopicMastery.mastery_probability.asc()

        )

        .all()

    )


    return [

        {

            "id":
                topic.id,

            "category":
                topic.category,

            "topic":
                topic.topic,

            "mastery_probability":
                topic.mastery_probability,

            "confidence":
                topic.confidence,

            "evidence_count":
                topic.evidence_count,

            "correct_evidence":
                topic.correct_evidence,

            "incorrect_evidence":
                topic.incorrect_evidence,

            "last_evidence_at":
                topic.last_evidence_at,

        }

        for topic in topics

    ]

@router.post(
    "/topics/{category}/{topic}/recalculate"
)
def recalculate_single_topic(

    category: str,

    topic: str,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    result = (

        knowledge_tracer
        .calculate_topic_mastery(

            db=db,

            user_id=user_id,

            category=category,

            topic=topic,

        )

    )

    return {

        "category":
            result.category,

        "topic":
            result.topic,

        "mastery_probability":
            result.mastery_probability,

        "confidence":
            result.confidence,

        "evidence_count":
            result.evidence_count,

        "correct_evidence":
            result.correct_evidence,

        "incorrect_evidence":
            result.incorrect_evidence,

    }

@router.post("/skills/seed")
def seed_skills(

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    created = (
        skill_seed_service.seed(
            db=db
        )
    )


    return {

        "created_skills":
            created,

    }