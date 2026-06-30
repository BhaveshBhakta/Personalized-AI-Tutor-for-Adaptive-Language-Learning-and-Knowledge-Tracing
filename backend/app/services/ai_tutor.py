from app.services.ai_agent import (
    AIAgent,
)


class AITutor:

    def __init__(self):

        self.agent = AIAgent()

    def ask(

        self,

        user_id: int,

        question: str,

        provider: str,

    ):

        return self.agent.answer(

            user_id,

            question,

            provider,

        )