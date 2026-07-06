from typing import Generator

from groq import Groq

import google.generativeai as genai

from app.core.config import settings


class LLMService:

    def __init__(self):

        self.groq_client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        genai.configure(
            api_key=settings.GEMINI_API_KEY
        )


    def ask_groq(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
    ) -> str:

        response = (
            self.groq_client
            .chat
            .completions
            .create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )


    def stream_groq(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
    ) -> Generator[str, None, None]:

        stream = (
            self.groq_client
            .chat
            .completions
            .create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
                stream=True,
            )
        )

        for chunk in stream:

            content = (
                chunk
                .choices[0]
                .delta
                .content
            )

            if content:
                yield content


    def ask_gemini(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
    ) -> str:

        gemini_model = genai.GenerativeModel(
            model
        )

        response = (
            gemini_model.generate_content(
                prompt
            )
        )

        return response.text


    def stream_gemini(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
    ) -> Generator[str, None, None]:

        gemini_model = genai.GenerativeModel(
            model
        )

        response = (
            gemini_model.generate_content(
                prompt,
                stream=True,
            )
        )

        for chunk in response:

            if chunk.text:
                yield chunk.text


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


    def stream(
        self,
        prompt: str,
        provider: str = "groq",
    ) -> Generator[str, None, None]:

        if provider == "gemini":

            yield from self.stream_gemini(
                prompt
            )

            return

        yield from self.stream_groq(
            prompt
        )