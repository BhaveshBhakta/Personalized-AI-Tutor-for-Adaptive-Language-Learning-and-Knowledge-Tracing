interface ChatBubbleProps {

  role: "user" | "assistant";

  content: string;

}

export default function ChatBubble({

  role,

  content,

}: ChatBubbleProps) {

  const isUser = role === "user";

  return (

    <div
      className={
        isUser
          ? "flex justify-end"
          : "flex justify-start"
      }
    >

      <div
        className={
          isUser
            ? `
              max-w-[80%]
              rounded-2xl
              bg-blue-600
              text-white
              px-5
              py-3
              shadow
            `
            : `
              max-w-[80%]
              rounded-2xl
              bg-gray-100
              text-black
              px-5
              py-3
              shadow
            `
        }
      >

        <div
          className="
            text-xs
            font-semibold
            mb-2
            opacity-70
          "
        >
          {isUser ? "You" : "German AI"}
        </div>

        <div
          className="
            whitespace-pre-wrap
            leading-7
          "
        >
          {content}
        </div>

      </div>

    </div>

  );

}