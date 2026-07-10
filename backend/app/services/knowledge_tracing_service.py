from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.orm import Session

from app.models.topic_mastery import (
    TopicMastery,
)

from app.services.mastery_evidence_service import (
    MasteryEvidenceService,
)

from app.services.skill_mapping_service import (
    SkillMappingService,
)

import math

class KnowledgeTracingService:


    INITIAL_MASTERY = 0.30

    LEARNING_RATE = 0.18

    FAILURE_RATE = 0.14

    FORGETTING_HALF_LIFE_DAYS = 45.0


    def __init__(self):

        self.evidence_service = (
            MasteryEvidenceService()
        )

        self.skill_mapper = (
            SkillMappingService()
        )


    def update_probability(

        self,

        current_mastery: float,

        evidence_value: float,

        evidence_weight: float,

    ) -> float:


        weight = max(
            0.1,
            min(
                evidence_weight,
                2.0,
            ),
        )


        if evidence_value >= 0.7:

            gain = (

                self.LEARNING_RATE

                * weight

                * (
                    1.0
                    - current_mastery
                )

            )


            new_mastery = (

                current_mastery
                + gain

            )


        elif evidence_value < 0.5:

            loss = (

                self.FAILURE_RATE

                * weight

                * current_mastery

            )


            new_mastery = (

                current_mastery
                - loss

            )


        else:

            new_mastery = (
                current_mastery
            )


        return max(

            0.01,

            min(
                new_mastery,
                0.99,
            ),

        )

    def apply_recency_decay(

        self,

        mastery: float,

        last_evidence_at,

    ) -> float:


        if not last_evidence_at:

            return mastery


        now = datetime.utcnow()


        elapsed_days = max(

            0.0,

            (
                now
                - last_evidence_at
            ).total_seconds()
            / 86400.0,

        )


        if elapsed_days <= 1.0:

            return mastery


        decay_factor = math.pow(

            0.5,

            elapsed_days
            / self.FORGETTING_HALF_LIFE_DAYS,

        )


        baseline = (
            self.INITIAL_MASTERY
        )


        decayed_mastery = (

            baseline

            + (
                mastery
                - baseline
            )
            * decay_factor

        )


        return max(

            0.01,

            min(
                decayed_mastery,
                0.99,
            ),

        )

    def calculate_topic_mastery(

        self,

        db: Session,

        user_id: int,

        category: str,

        topic: str,

    ) -> TopicMastery:


        evidence = (

            self.evidence_service
            .collect_topic_evidence(

                db=db,

                user_id=user_id,

                category=category,

                topic=topic,

            )

        )


        mastery = (
            self.INITIAL_MASTERY
        )


        correct_count = 0

        incorrect_count = 0


        chronological_evidence = list(
            reversed(
                evidence
            )
        )


        for item in chronological_evidence:


            mastery = (
                self.update_probability(

                    current_mastery=
                        mastery,

                    evidence_value=
                        item["value"],

                    evidence_weight=
                        item["weight"],

                )
            )


            if item["is_positive"]:

                correct_count += 1

            else:

                incorrect_count += 1

            if evidence:

                mastery = (
                    self.apply_recency_decay(

                        mastery=mastery,

                        last_evidence_at=
                            evidence[0][
                                "created_at"
                            ],

                    )
                )
                
        evidence_count = len(
            evidence
        )


        confidence = min(

            1.0,

            evidence_count / 10.0,

        )


        mastery_record = (

            db.query(
                TopicMastery
            )

            .filter(

                TopicMastery.user_id
                == user_id,

                TopicMastery.skill_id
                == skill.id,

            )

            .first()

        )


        if not mastery_record:

            mastery_record = TopicMastery(

                user_id=user_id,

                skill_id=skill.id,

                category=
                    skill.category,

                topic=
                    skill.name,

            )

            db.add(
                mastery_record
            )


        mastery_record.mastery_probability = (
            mastery
        )


        mastery_record.confidence = (
            confidence
        )


        mastery_record.evidence_count = (
            evidence_count
        )


        mastery_record.correct_evidence = (
            correct_count
        )


        mastery_record.incorrect_evidence = (
            incorrect_count
        )


        mastery_record.last_evidence_at = (

            evidence[0]["created_at"]

            if evidence

            else None

        )


        mastery_record.updated_at = (
            datetime.utcnow()
        )


        db.commit()

        db.refresh(
            mastery_record
        )


        return mastery_record