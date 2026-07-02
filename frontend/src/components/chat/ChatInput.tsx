import { useState } from "react";

interface ChatInputProps {

  onSend: (
    message: string
  ) => void;

  loading: boolean;

}

export default function ChatInput({

  onSend,

  loading,

}: ChatInputProps) {

  const [message, setMessage] =
    useState("");

  function send() {

    if (!message.trim()) return;

    onSend(message);

    setMessage("");

  }

  return (

    <div
      className="
        flex
        gap-3
        mt-6
      "
    >

      <textarea

        value={message}

        onChange={(e)=>
          setMessage(
            e.target.value
          )
        }

        onKeyDown={(e)=>{

          if(
            e.key==="Enter"
            &&
            !e.shiftKey
          ){

            e.preventDefault();

            send();

          }

        }}

        placeholder="Ask anything about German..."

        rows={2}

        className="
          flex-1
          resize-none
          rounded-xl
          border
          p-4
          focus:outline-none
          focus:ring-2
          focus:ring-blue-500
        "

      />

      <button

        disabled={loading}

        onClick={send}

        className="
          rounded-xl
          bg-blue-600
          px-8
          text-white
          disabled:opacity-50
        "

      >

        {

          loading

          ? "..."

          : "Send"

        }

      </button>

    </div>

  );

}