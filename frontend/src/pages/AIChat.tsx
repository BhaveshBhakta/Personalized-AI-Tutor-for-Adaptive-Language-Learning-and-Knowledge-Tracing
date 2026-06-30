import { useState } from "react";
import { api } from "../api/client";
import ChatBubble from "../components/chat/ChatBubble";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AIChat() {

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [question, setQuestion] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [provider, setProvider] =
    useState("groq");

  async function sendMessage() {

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

      const assistant: Message = {

        role: "assistant",

        content:
          res.data.answer ??
          "No response.",

      };

      setMessages((prev) => [

        ...prev,

        assistant,

      ]);

    } catch {

      setMessages((prev) => [

        ...prev,

        {

          role: "assistant",

          content:
            "Something went wrong.",

        },

      ]);

    }

    setQuestion("");

    setLoading(false);

  }

  return (

    <div className="max-w-5xl mx-auto p-8">

      <h1 className="text-4xl font-bold mb-2">

        🤖 German AI Tutor

      </h1>

      <p className="text-gray-500 mb-8">

        Ask anything about German.

      </p>

      <div className="mb-6">

        <select

          value={provider}

          onChange={(e)=>
            setProvider(
              e.target.value
            )
          }

          className="
            border
            rounded
            p-2
          "

        >

          <option value="groq">

            Groq

          </option>

          <option value="gemini">

            Gemini

          </option>

        </select>

      </div>

      <div
        className="
          border
          rounded-xl
          h-[500px]
          overflow-y-auto
          p-6
          space-y-6
          bg-white
        "
      >

        {

          messages.length === 0 && (

            <div
              className="
                text-center
                text-gray-400
                mt-40
              "
            >

              Start a conversation 👋

            </div>

          )

        }

        {

          messages.map(

            (msg, index)=>(

             <ChatBubble
                key={index}
                role={msg.role}
                content={msg.content}
                />
            )

          )

        }

        {

          loading && (

            <div>

              AI is thinking...

            </div>

          )

        }

      </div>

      <div
        className="
          flex
          gap-3
          mt-6
        "
      >

        <input

          value={question}

          onChange={(e)=>

            setQuestion(
              e.target.value
            )

          }

          onKeyDown={(e)=>{

            if(e.key==="Enter"){

              sendMessage();

            }

          }}

          placeholder="Ask your German question..."

          className="
            flex-1
            border
            rounded-xl
            p-4
          "

        />

        <button

          onClick={sendMessage}

          className="
            bg-black
            text-white
            px-8
            rounded-xl
          "

        >

          Send

        </button>

      </div>

    </div>

  );

}