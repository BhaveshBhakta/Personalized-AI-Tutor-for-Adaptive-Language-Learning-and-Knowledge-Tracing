import json

from app.services.llm_service import (
    LLMService,
)


class LearningSignalDetector:


    ALLOWED_SIGNAL_TYPES = {

        "grammar_confusion",
        "vocabulary_confusion",
        "repeated_mistake",
        "correction_success",
        "concept_understood",

    }


    ALLOWED_CATEGORIES = {

        "grammar",
        "vocabulary",
        "conversation",
        "general",

    }


    def __init__(self):

        self.llm = LLMService()


    def detect(

        self,

        question: str,

        answer: str,

        provider: str = "groq",

    ) -> list[dict]:


        prompt = f"""
You analyze a German learner interaction.

Your task is to identify learning signals.

LEARNER MESSAGE:

{question}

TUTOR RESPONSE:

{answer}


Return ONLY valid JSON.

The exact format must be:

{{
  "signals": [
    {{
      "signal_type": "grammar_confusion",
      "category": "grammar",
      "topic": "accusative case",
      "evidence": "short explanation",
      "confidence": 0.85
    }}
  ]
}}


Allowed signal_type values:

- grammar_confusion
- vocabulary_confusion
- repeated_mistake
- correction_success
- concept_understood


Allowed category values:

- grammar
- vocabulary
- conversation
- general


Rules:

1. Do not create a signal merely because the learner asks
   a normal informational question.

2. grammar_confusion requires evidence of misunderstanding,
   incorrect usage, or explicit confusion.

3. vocabulary_confusion requires evidence of misunderstanding
   a word, meaning, article, plural, or usage.

4. repeated_mistake should only be returned when the interaction
   itself provides reasonable evidence of repetition.

5. correction_success requires evidence that the learner corrected
   an earlier mistake successfully.

6. concept_understood requires evidence that the learner demonstrates
   understanding, not merely says "ok".

7. confidence must be between 0 and 1.

8. If there is no meaningful learning signal, return:

{{
  "signals": []
}}
"""


        raw_response = self.llm.ask(

            prompt=prompt,

            provider=provider,

        )


        try:

            data = json.loads(
                raw_response
            )

        except json.JSONDecodeError:

            return []


        signals = data.get(
            "signals",
            []
        )


        validated = []


        for signal in signals:

            signal_type = signal.get(
                "signal_type"
            )

            category = signal.get(
                "category"
            )

            topic = str(
                signal.get(
                    "topic",
                    ""
                )
            ).strip()


            if (
                signal_type
                not in self.ALLOWED_SIGNAL_TYPES
            ):

                continue


            if (
                category
                not in self.ALLOWED_CATEGORIES
            ):

                continue


            if not topic:

                continue


            try:

                confidence = float(
                    signal.get(
                        "confidence",
                        0.5,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                confidence = 0.5


            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0,
                ),
            )


            validated.append({

                "signal_type":
                    signal_type,

                "category":
                    category,

                "topic":
                    topic,

                "evidence":
                    signal.get(
                        "evidence"
                    ),

                "confidence":
                    confidence,

            })


        return validated