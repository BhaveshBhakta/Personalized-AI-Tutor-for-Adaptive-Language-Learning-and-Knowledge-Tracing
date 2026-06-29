from app.services.llm_service import (
    LLMService,
)

from app.services.prompt_builder import (
    PromptBuilder,
)

from app.services.retriever import (
    Retriever,
)


class AIOrchestrator:

    def __init__(self):

        self.retriever = Retriever()

        self.prompt_builder = (
            PromptBuilder()
        )

        self.llm = LLMService()

    def ask(

        self,

        question: str,

        provider: str = "groq",

    ):

        context = (
            self.retriever.retrieve_context(
                question
            )
        )

        prompt = (
            self.prompt_builder.build_rag_prompt(

                question,

                context,

            )
        )

        answer = self.llm.ask(

            prompt,

            provider,

        )

        return {

            "question":
            question,

            "context":
            context,

            "answer":
            answer,

        }