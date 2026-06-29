class PromptBuilder:

    @staticmethod
    def build_rag_prompt(

        question: str,

        context: str,

    ) -> str:

        return f"""
You are an expert German language tutor.

Your job is to teach German in a clear,
patient and beginner-friendly manner.

Use ONLY the provided context.

If the answer cannot be found,
say that you do not know.

Explain using:

• Simple English

• German examples

• Grammar explanation

• Learning tips

----------------------------

Context:

{context}

----------------------------

Question:

{question}

----------------------------

Answer:
"""