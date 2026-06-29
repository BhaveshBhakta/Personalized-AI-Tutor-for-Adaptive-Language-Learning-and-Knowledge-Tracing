import os

from groq import Groq

import google.generativeai as genai


class LLMService:

    def __init__(self):

        self.groq_client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )

        genai.configure(
            api_key=os.getenv(
                "GEMINI_API_KEY"
            )
        )

    def ask_groq(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
    ) -> str:

        response = (
            self.groq_client.chat.completions.create(

                model=model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],

                temperature=0.3,

            )
        )

        return response.choices[0].message.content

    def ask_gemini(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
    ) -> str:

        model = genai.GenerativeModel(
            model
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    def ask(
        self,
        prompt: str,
        provider: str = "groq",
    ) -> str:

        if provider == "gemini":

            return self.ask_gemini(
                prompt
            )

        return self.ask_groq(
            prompt
        )