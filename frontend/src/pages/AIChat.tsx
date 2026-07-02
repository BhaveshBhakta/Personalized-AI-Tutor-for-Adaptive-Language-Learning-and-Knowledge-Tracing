import { useState } from "react";

import { api } from "../api/client";

import ChatBubble from "../components/chat/ChatBubble";
import ChatInput from "../components/chat/ChatInput";
import ChatSidebar from "../components/chat/ChatSidebar";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AIChat() {

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [provider, setProvider] =
    useState("groq");

  async function sendMessage(
    question: string
  ) {

    if (!question.trim()) return;

    const userMessage: Message = {

      role: "user",

      content: question,

    };

    setMessages((prev) => [

      ...prev,

      userMessage,

    ]);

    setLoading(true);

    const token =
      localStorage.getItem("token");

    try {

      const res = await api.post(

        "/ai/ask",

        {

          question,

          provider,

        },

        {

          headers: {

            Authorization:
              `Bearer ${token}`,

          },

        }

      );

      const assistantMessage: Message = {

        role: "assistant",

        content:

          res.data.answer ??

          "No response received.",

      };

      setMessages((prev) => [

        ...prev,

        assistantMessage,

      ]);

    }

    catch {

      setMessages((prev) => [

        ...prev,

        {

          role: "assistant",

          content:

            "Something went wrong while contacting the AI.",

        },

      ]);

    }

    finally {

      setLoading(false);

    }

  }

  return (

    <div className="flex h-screen bg-gray-50">

      <ChatSidebar

        provider={provider}

        setProvider={setProvider}

      />

      <div
        className="
          flex-1
          flex
          flex-col
          p-8
        "
      >

        <div className="mb-6">

          <h1
            className="
              text-4xl
              font-bold
            "
          >

            🤖 German AI Tutor

          </h1>

          <p
            className="
              text-gray-500
              mt-2
            "
          >

            Ask anything about German grammar,
            vocabulary, pronunciation,
            Goethe exams or your uploaded PDFs.

          </p>

        </div>

        <div
          className="
            flex-1
            overflow-y-auto
            rounded-xl
            border
            bg-white
            p-6
            space-y-6
            shadow-sm
          "
        >

          {

            messages.length === 0 && (

              <div
                className="
                  h-full
                  flex
                  items-center
                  justify-center
                  text-gray-400
                "
              >

                Start a conversation 👋

              </div>

            )

          }

          {

            messages.map(

              (

                message,

                index

              ) => (

                <ChatBubble

                  key={index}

                  role={message.role}

                  content={message.content}

                />

              )

            )

          }

          {

            loading && (

              <div
                className="
                  text-gray-500
                  italic
                "
              >

                AI is thinking...

              </div>

            )

          }

        </div>

        <ChatInput

          loading={loading}

          onSend={sendMessage}

        />

      </div>

    </div>

  );

}