from app.services.ai_orchestrator import (
    AIOrchestrator,
)


class AITutor:

    def __init__(self):

        self.ai = AIOrchestrator()

    def ask(

        self,

        user_id: int,

        question: str,

        provider: str,

    ):

        return self.ai.ask(

            user_id=user_id,

            question=question,

            provider=provider,

        )