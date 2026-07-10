import re

from sqlalchemy.orm import Session

from app.models.skill import Skill

from app.models.skill_alias import (
    SkillAlias,
)


class SkillMappingService:


    def normalize(
        self,
        value: str,
    ) -> str:

        value = value.strip().lower()

        value = re.sub(
            r"[^a-zäöüß0-9\s-]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()


    def get_or_create_skill(

        self,

        db: Session,

        category: str,

        topic: str,

        level: str = "A1",

    ) -> Skill:


        normalized_topic = (
            self.normalize(topic)
        )


        alias = (

            db.query(
                SkillAlias
            )

            .filter(

                SkillAlias.category
                == category,

                SkillAlias.normalized_alias
                == normalized_topic,

            )

            .first()

        )


        if alias:

            return (

                db.query(
                    Skill
                )

                .filter(
                    Skill.id
                    == alias.skill_id
                )

                .first()

            )


        skill_key = (

            category.strip().lower()

            + "."

            + normalized_topic
            .replace(
                " ",
                "_",
            )

        )


        skill = (

            db.query(
                Skill
            )

            .filter(

                Skill.skill_key
                == skill_key

            )

            .first()

        )


        if not skill:

            skill = Skill(

                skill_key=
                    skill_key,

                category=
                    category,

                name=
                    topic.strip(),

                level=
                    level,

            )

            db.add(skill)

            db.flush()


        existing_alias = (

            db.query(
                SkillAlias
            )

            .filter(

                SkillAlias.category
                == category,

                SkillAlias.normalized_alias
                == normalized_topic,

            )

            .first()

        )


        if not existing_alias:

            alias = SkillAlias(

                skill_id=
                    skill.id,

                category=
                    category,

                alias=
                    topic.strip(),

                normalized_alias=
                    normalized_topic,

            )

            db.add(alias)


        db.commit()

        db.refresh(skill)


        return skill