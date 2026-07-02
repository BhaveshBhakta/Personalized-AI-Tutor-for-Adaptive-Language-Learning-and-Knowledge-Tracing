interface ChatSidebarProps {

  provider: string;

  setProvider: (
    provider: string
  ) => void;

}

export default function ChatSidebar({

  provider,

  setProvider,

}: ChatSidebarProps) {

  return (

    <div
      className="
        w-72
        border-r
        h-screen
        p-5
        flex
        flex-col
      "
    >

      <button
        className="
          w-full
          rounded-xl
          bg-black
          text-white
          py-3
          mb-8
        "
      >
        + New Chat
      </button>

      <div
        className="
          text-sm
          font-semibold
          text-gray-500
          mb-4
        "
      >
        Recent Chats
      </div>

      <div className="space-y-2">

        <button
          className="
            w-full
            rounded-lg
            border
            p-3
            text-left
          "
        >
          German Articles
        </button>

        <button
          className="
            w-full
            rounded-lg
            border
            p-3
            text-left
          "
        >
          Vocabulary Help
        </button>

        <button
          className="
            w-full
            rounded-lg
            border
            p-3
            text-left
          "
        >
          Goethe A1
        </button>

      </div>

      <div className="flex-1" />

      <div className="mb-3 font-semibold">

        AI Provider

      </div>

      <select

        value={provider}

        onChange={(e)=>

          setProvider(
            e.target.value
          )

        }

        className="
          rounded-lg
          border
          p-3
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

  );

}