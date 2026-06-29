from app.services.ai_orchestrator import (
    AIOrchestrator,
)


class AITutor:

    def __init__(self):

        self.ai = AIOrchestrator()

    def ask(

        self,

        question: str,

        provider: str = "groq",

    ):

        return self.ai.ask(

            question,

            provider,

        )