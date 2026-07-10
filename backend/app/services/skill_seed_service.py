from sqlalchemy.orm import Session

from app.models.skill import Skill

from app.models.skill_alias import (
    SkillAlias,
)

from app.services.skill_mapping_service import (
    SkillMappingService,
)


class SkillSeedService:


    SKILLS = [

        {

            "skill_key":
                "grammar.nominative",

            "category":
                "grammar",

            "name":
                "Nominative Case",

            "level":
                "A1",

            "aliases": [

                "nominative",

                "nominativ",

                "german nominative",

                "nominative case",

            ],

        },

        {

            "skill_key":
                "grammar.accusative",

            "category":
                "grammar",

            "name":
                "Accusative Case",

            "level":
                "A1",

            "aliases": [

                "accusative",

                "akkusativ",

                "german accusative",

                "accusative case",

            ],

        },

        {

            "skill_key":
                "grammar.dative",

            "category":
                "grammar",

            "name":
                "Dative Case",

            "level":
                "A2",

            "aliases": [

                "dative",

                "dativ",

                "german dative",

                "dative case",

                "dative articles",

            ],

        },

        {

            "skill_key":
                "grammar.word_order",

            "category":
                "grammar",

            "name":
                "German Word Order",

            "level":
                "A1",

            "aliases": [

                "word order",

                "german word order",

                "sentence structure",

                "satzbau",

            ],

        },

        {

            "skill_key":
                "grammar.article_gender",

            "category":
                "grammar",

            "name":
                "Article and Noun Gender",

            "level":
                "A1",

            "aliases": [

                "der die das",

                "articles",

                "noun gender",

                "german gender",

                "article gender",

            ],

        },

    ]


    def __init__(self):

        self.mapper = (
            SkillMappingService()
        )


    def seed(

        self,

        db: Session,

    ) -> int:


        created_count = 0


        for data in self.SKILLS:


            skill = (

                db.query(
                    Skill
                )

                .filter(

                    Skill.skill_key
                    == data["skill_key"]

                )

                .first()

            )


            if not skill:

                skill = Skill(

                    skill_key=
                        data["skill_key"],

                    category=
                        data["category"],

                    name=
                        data["name"],

                    level=
                        data["level"],

                )

                db.add(skill)

                db.flush()

                created_count += 1


            for alias_text in data[
                "aliases"
            ]:


                normalized = (
                    self.mapper.normalize(
                        alias_text
                    )
                )


                exists = (

                    db.query(
                        SkillAlias
                    )

                    .filter(

                        SkillAlias.category
                        == data["category"],

                        SkillAlias.normalized_alias
                        == normalized,

                    )

                    .first()

                )


                if not exists:

                    db.add(

                        SkillAlias(

                            skill_id=
                                skill.id,

                            category=
                                data[
                                    "category"
                                ],

                            alias=
                                alias_text,

                            normalized_alias=
                                normalized,

                        )

                    )


        db.commit()


        return created_count