from app.services.llm_service import (
    LLMService,
)

from app.services.memory_service import (
    MemoryService,
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

        self.memory = MemoryService()

        self.prompt_builder = (
            PromptBuilder()
        )

        self.llm = LLMService()

    def ask(

        self,

        user_id: int,

        question: str,

        provider: str = "groq",

    ):

        context = (
            self.retriever.retrieve_context(
                question
            )
        )

        history = self.memory.get_history(
            user_id
        )

        history_text = ""

        for msg in history:

            history_text += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        prompt = (
            self.prompt_builder.build_rag_prompt(
                question=question,
                context=context,
            )
        )

        final_prompt = f"""
Conversation History:

{history_text}

-------------------

{prompt}
"""

        answer = self.llm.ask(

            prompt=final_prompt,

            provider=provider,

        )

        self.memory.add_message(

            user_id,

            "user",

            question,

        )

        self.memory.add_message(

            user_id,

            "assistant",

            answer,

        )

        return {

            "question": question,

            "context": context,

            "answer": answer,

        }