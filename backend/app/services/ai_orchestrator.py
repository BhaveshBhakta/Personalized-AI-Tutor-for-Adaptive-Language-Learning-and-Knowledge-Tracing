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

                    max_distance=
                        YOUR_TESTED_THRESHOLD,

                    max_context_chars=
                        12000,

                    max_chunks_per_document=
                        3,

                    overlap_threshold=
                        0.85,

                )

            )


            context = retrieval[
                "context"
            ]


            sources = retrieval[
                "sources"
            ]


            has_evidence = retrieval.get(

                "has_evidence",

                False,

            )


            best_distance = retrieval.get(

                "best_distance"

            )


        else:

            context = ""

            sources = []

            has_evidence = False

            best_distance = None

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

        evidence_available = (

            document_mode

            and has_evidence

        )


        if (
            document_mode
            and evidence_available
        ):

            grounding_instruction = """
        DOCUMENT MODE IS ACTIVE.

        The learner selected one or more uploaded documents,
        and retrieved document evidence is available.

        Rules:

        1. Use the retrieved document context as the primary factual source
        for claims about the selected documents.

        2. Do not claim that a document says something unless that claim is
        supported by the retrieved context.

        3. Do not add a manual Sources section to the answer.
        Sources are displayed separately by the interface.

        4. If the retrieved evidence only partially answers the question,
        clearly separate:
        - what the documents support;
        - what is general knowledge.

        5. Conversation history remains authoritative for conversational
        references such as:
        "those examples",
        "the second one",
        "that sentence",
        and similar follow-up references.
        """


        elif (
            document_mode
            and not evidence_available
        ):

            grounding_instruction = """
        DOCUMENT MODE IS ACTIVE, BUT NO USABLE DOCUMENT EVIDENCE
        WAS RETRIEVED.

        Rules:

        1. Do not pretend that the selected documents contain the answer.

        2. Clearly state that the available document evidence does not
        provide enough information to answer from the selected documents.

        3. If useful, you may provide a separate general explanation,
        but clearly label it as general knowledge rather than information
        from the selected documents.

        4. Do not invent document claims, quotations, page references,
        filenames, or citations.

        5. Do not add a manual Sources section.
        """


        else:

            grounding_instruction = """
        GENERAL TUTOR MODE IS ACTIVE.

        Answer as an expert German language tutor.

        Do not claim to use uploaded documents because no document mode
        is active.

        Use conversation history to resolve follow-up references and preserve
        the learner's current topic.
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
   NEVER use SOURCE numbering, chunk numbering, or document order
   to resolve conversational references such as "the second one".

5. When the learner asks to simplify, transform, compare, or explain
   previous content, preserve the subject of the immediately previous
   tutor response.

6. Do not invent document claims.

7. Keep the answer focused and avoid unnecessary repetition.

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