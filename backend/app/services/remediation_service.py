from app.services.llm_service import (
    LLMService,
)


class RemediationService:

    def __init__(self):

        self.llm = LLMService()


    def generate(

        self,

        category: str,

        topic: str,

        provider: str = "groq",

    ) -> str:

        prompt = f"""
You are an expert German tutor.

The learner has repeatedly struggled with this topic.

Category:
{category}

Topic:
{topic}

Create a short remediation lesson.

Requirements:

1. Explain the concept simply.
2. Give one easy rule.
3. Give three examples.
4. Explain one common mistake.
5. Give one memory trick.
6. End with one practice question.

Return Markdown.
"""

        return self.llm.ask(

            prompt=prompt,

            provider=provider,

        )