from typing import Generator
import json
from sqlalchemy.orm import Session

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


    def build_prompt(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

        question: str,

        document_ids:
            list[int] | None = None,

    ):

        if document_ids:

            retrieval = (

                self.retriever
                .retrieve_with_sources(

                    query=question,

                    user_id=user_id,

                    document_ids=
                        document_ids,

                    top_k=5,

                )

            )


            context = retrieval[
                "context"
            ]


            sources = retrieval[
                "sources"
            ]


        else:

            context = ""

            sources = []


        history = (

            self.memory
            .get_history(

                db=db,

                conversation_id=
                    conversation_id,

                limit=12,

            )

        )


        history_text = ""


        for index, msg in enumerate(

            history,

            start=1,

        ):

            role = (

                "LEARNER"

                if msg["role"] == "user"

                else "TUTOR"

            )


            history_text += (

                f"[MESSAGE {index} - {role}]\n"

                f"{msg['content']}\n"

                f"[END MESSAGE {index}]\n\n"

            )


        recent_exchange_text = ""


        if history:

            recent_messages = (
                history[-2:]
            )


            for msg in recent_messages:

                role = (

                    "LEARNER"

                    if msg["role"] == "user"

                    else "TUTOR"

                )


                recent_exchange_text += (

                    f"{role}:\n"

                    f"{msg['content']}\n\n"

                )


        document_mode = bool(
            document_ids
        )


        if document_mode:

            grounding_instruction = """
DOCUMENT MODE IS ACTIVE.

The learner selected one or more uploaded documents.

Rules:
1. Use the retrieved document context as the primary factual source.
2. Do not claim that a document says something unless it appears in the retrieved context.
3. When using information from a document, mention the source filename naturally.
4. If the selected documents do not contain enough information, clearly say so.
5. Conversation history is still authoritative for references such as:
   "those examples", "that sentence", "explain it again", and similar follow-ups.
"""

        else:

            grounding_instruction = """
GENERAL TUTOR MODE IS ACTIVE.

Answer as an expert German language tutor.

Retrieved document context may be empty or unrelated.
Do not force document information into the answer when it is not relevant.
"""


        final_prompt = f"""
You are an adaptive German language tutor.

Your job is to help the learner understand German accurately,
clearly, and according to the ongoing conversation.

{grounding_instruction}

IMPORTANT CONVERSATION RULES:

1. First interpret the learner's current question using the MOST RECENT
   EXCHANGE.

2. References such as:
   - "the first one"
   - "the second one"
   - "the third example"
   - "those examples"
   - "these examples"
   - "that sentence"
   - "that rule"
   - "explain it again"
   - "make that easier"

   refer to the immediately previous tutor response unless the learner
   explicitly refers to an older topic.

3. Only use older conversation history if the immediately previous
   exchange does not contain the referenced information.

4. Retrieved document context is factual reference material.
   NEVER use the structure, numbering, bullet order, or section order
   of retrieved document context to resolve conversational references
   such as "the second one", "the third example", or "that sentence".

5. When the learner asks to simplify, transform, compare, or explain
   previous content, preserve the subject of the immediately previous
   tutor response.

6. Preserve the requested number of examples or items when transforming
   earlier content.

7. Do not invent a different previous answer or silently switch to an
   unrelated document section.

8. Keep answers focused. Do not repeat the same sentence, correction,
   explanation, or example multiple times.r.

FULL CONVERSATION HISTORY:

{history_text if history_text else "No previous conversation history."}

--------------------------------------------------

MOST RECENT EXCHANGE:

{recent_exchange_text if recent_exchange_text else "No previous exchange."}

--------------------------------------------------

CURRENT LEARNER QUESTION:

{question}

--------------------------------------------------

RETRIEVED DOCUMENT CONTEXT:

{context if context else "No relevant document context was retrieved."}

--------------------------------------------------

ANSWER INSTRUCTIONS:

Answer the current learner question directly.

When useful:
- give German examples;
- provide English translations;
- explain grammar clearly;
- correct mistakes politely;
- use Markdown formatting for readability.

For German grammar:
- verify case and article forms carefully;
- dative plural definite article is "den";
- mention plural noun "-n" where applicable.
"""


        return (
            final_prompt,
            context,
            sources,
        )


    def ask(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

        question: str,

        provider: str = "groq",

        document_ids:
            list[int] | None = None,

    ):

        (
            final_prompt,
            context,
            sources,
        ) = self.build_prompt(

            db=db,

            user_id=user_id,

            conversation_id=
                conversation_id,

            question=question,

            document_ids=
                document_ids,

        )


        self.memory.add_message(

            db=db,

            conversation_id=
                conversation_id,

            role="user",

            content=question,

        )


        answer = self.llm.ask(

            prompt=final_prompt,

            provider=provider,

        )


        self.memory.add_message(

            db=db,

            conversation_id=
                conversation_id,

            role="assistant",

            content=answer,

            sources=sources,

        )


        return {

            "question":
                question,

            "context":
                context,

            "sources":
                sources,

            "answer":
                answer,

        }


    def stream_answer(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

        question: str,

        provider: str = "groq",

        document_ids:
            list[int] | None = None,

    ) -> Generator[str, None, None]:


        (
            final_prompt,
            _,
            sources,
        ) = self.build_prompt(

            db=db,

            user_id=user_id,

            conversation_id=
                conversation_id,

            question=question,

            document_ids=
                document_ids,

        )


        self.memory.add_message(

            db=db,

            conversation_id=
                conversation_id,

            role="user",

            content=question,

        )


        complete_answer = ""

        completed = False


        try:

            for chunk in self.llm.stream(

                prompt=final_prompt,

                provider=provider,

            ):

                complete_answer += chunk


                event = {

                    "type":
                        "token",

                    "content":
                        chunk,

                }


                yield (
                    json.dumps(
                        event
                    )
                    + "\n"
                )


            completed = True


            if sources:

                source_event = {

                    "type":
                        "sources",

                    "sources":
                        sources,

                }


                yield (
                    json.dumps(
                        source_event
                    )
                    + "\n"
                )


            done_event = {

                "type":
                    "done",

            }


            yield (
                json.dumps(
                    done_event
                )
                + "\n"
            )


        finally:

            if (
                completed
                and complete_answer.strip()
            ):

                self.memory.add_message(

                    db=db,

                    conversation_id=
                        conversation_id,

                    role="assistant",

                    content=
                        complete_answer,

                    sources=
                        sources,

                )