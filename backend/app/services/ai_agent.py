from app.services.memory_service import (
    MemoryService,
)

from app.services.prompt_builder import (
    PromptBuilder,
)

from app.services.retriever import (
    Retriever,
)

from app.services.llm_service import (
    LLMService,
)


class AIAgent:

    def __init__(self):

        self.memory = MemoryService()

        self.retriever = Retriever()

        self.prompts = PromptBuilder()

        self.llm = LLMService()

    def answer(

        self,

        user_id: int,

        question: str,

        provider: str,

    ):

        history = self.memory.get_history(
            user_id
        )

        context = self.retriever.retrieve_context(
            question
        )

        prompt = self.prompts.build_rag_prompt(

            question=question,

            context=context,

        )

        conversation = ""

        for item in history:

            conversation += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

        final_prompt = f"""

Conversation History

{conversation}

---------------------------------

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

            "answer": answer,

            "context": context,

        }