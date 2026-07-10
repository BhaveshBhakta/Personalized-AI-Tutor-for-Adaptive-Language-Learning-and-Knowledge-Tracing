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

from app.services.learner_state_service import (
    LearnerStateService,
)

from app.services.learning_signal_detector import (
    LearningSignalDetector,
)

from app.services.learning_signal_service import (
    LearningSignalService,
)

class AIOrchestrator:


    def __init__(self):

        self.retriever = Retriever()

        self.memory = MemoryService()

        self.prompt_builder = (
            PromptBuilder()
        )

        self.llm = LLMService()

        self.learner_state = (
            LearnerStateService()
        )

        self.signal_detector = (
            LearningSignalDetector()
        )

        self.signal_service = (
            LearningSignalService()
        )


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
                        None,

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


        learner_context = (

            self.learner_state
            .get_state(

                db=db,

                user_id=user_id,

            )

        )


        profile = learner_context[
            "profile"
        ]


        weak_grammar = learner_context[
            "weak_grammar"
        ]


        grammar_context_text = ""


        if weak_grammar:

            for item in weak_grammar:

                grammar_context_text += (

                    f"- Grammar topic ID: "
                    f"{item['topic_id']}\n"

                    f"  Mastery: "
                    f"{item['mastery_score']}%\n"

                    f"  Accuracy: "
                    f"{item['accuracy']}%\n"

                )

        else:

            grammar_context_text = (

                "No weak grammar topics "
                "have been identified yet."

            )


        weak_vocabulary = learner_context[
            "weak_vocabulary"
        ]


        vocabulary_context_text = ""


        if weak_vocabulary:

            for item in weak_vocabulary:

                display_word = item[
                    "word"
                ]


                if item.get(
                    "article"
                ):

                    display_word = (

                        f"{item['article']} "
                        f"{item['word']}"

                    )


                vocabulary_context_text += (

                    f"- {display_word}"
                    f" = {item['translation']}\n"

                    f"  Mastery: "
                    f"{item['mastery_score']}%\n"

                    f"  Retrievability: "
                    f"{round(item['retrievability'] * 100, 1)}%\n"

                    f"  Lapses: "
                    f"{item['lapses']}\n"

                )

        else:

            vocabulary_context_text = (

                "No weak vocabulary has "
                "been identified yet."

            )


        history = (

            self.memory
            .get_history(

                db=db,

                conversation_id=
                    conversation_id,

                limit=12,

            )

        )

        recurring_weaknesses = learner_context[
            "recurring_weaknesses"
        ]


        weakness_context_text = ""


        if recurring_weaknesses:

            for weakness in recurring_weaknesses:

                weakness_context_text += (

                    f"- {weakness['topic']}\n"

                    f"  Category: "
                    f"{weakness['category']}\n"

                    f"  Pattern: "
                    f"{weakness['type']}\n"

                    f"  Occurrences: "
                    f"{weakness['occurrences']}\n"

                )

        else:

            weakness_context_text = (
                "No recurring mistake patterns "
                "have been detected yet."
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

LEARNER PROFILE:

Target German level:
{profile["target_level"]}

Daily study goal:
{profile["daily_goal_minutes"]} minutes

Current XP:
{profile["xp"]}

Current streak:
{profile["streak"]} days


KNOWN WEAK GRAMMAR AREAS:

{grammar_context_text}


KNOWN WEAK VOCABULARY:

{vocabulary_context_text}


OBSERVED LEARNING PATTERNS:

{weakness_context_text}


PERSONALIZATION RULES:

1. Adapt explanation difficulty to the learner's target level.

2. Use known weak vocabulary naturally when useful for examples,
   but do not force unrelated vocabulary into every answer.

3. If the current question concerns a known weak grammar area,
   explain it carefully and use additional examples.

4. Do not tell the learner that you are reading database scores.

5. Do not mention mastery percentages unless the learner explicitly
   asks about progress.

6. Personalization context should guide teaching strategy,
   not override the learner's current question.

7. The current learner question remains the highest-priority task.

8. If an observed recurring weakness is relevant to the current
   question, provide additional scaffolding and contrastive examples.

9. Do not repeatedly lecture the learner about known weaknesses.

10. When the learner demonstrates improvement, gradually reduce
    scaffolding.

11. Never mention internal signal names, confidence values,
    occurrence counts, or stored learner-state data.

12. Do not force personalization when the observed weakness is
    unrelated to the current question.

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


        signals = self.signal_detector.detect(

            question=question,

            answer=answer,

            provider=provider,

        )


        self.signal_service.record_signals(

            db=db,

            user_id=user_id,

            conversation_id=
                conversation_id,

            signals=signals,

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

                signals = self.signal_detector.detect(

                    question=question,

                    answer=complete_answer,

                    provider=provider,

                )


                self.signal_service.record_signals(

                    db=db,

                    user_id=user_id,

                    conversation_id=
                        conversation_id,

                    signals=signals,

                )