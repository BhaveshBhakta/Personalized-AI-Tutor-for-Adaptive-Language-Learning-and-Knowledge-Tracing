import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  api,
} from "../api/client";

import ChatBubble
  from "../components/chat/ChatBubble";


interface Message {

  id?: number;

  role:
  | "user"
  | "assistant";

  content: string;

}


interface Conversation {

  id: number;

  title: string;

  provider: string;

}

interface DocumentItem {
  id: number;
  filename: string;
  status: string;
}


export default function AIChat() {

  const [
    messages,
    setMessages,
  ] = useState<Message[]>([]);


  const [
    conversations,
    setConversations,
  ] = useState<Conversation[]>([]);


  const [
    conversationId,
    setConversationId,
  ] = useState<number | null>(
    null
  );


  const [
    question,
    setQuestion,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    provider,
    setProvider,
  ] = useState("groq");

  const [
    documents,
    setDocuments,
  ] = useState<DocumentItem[]>([]);

  const [
    selectedDocumentIds,
    setSelectedDocumentIds,
  ] = useState<number[]>([]);

  const bottomRef =
    useRef<HTMLDivElement | null>(
      null
    );

  const skipNextMessageLoadRef =
    useRef(false);


  async function loadConversations() {

    try {

      const res = await api.get(
        "/ai/conversations"
      );


      setConversations(
        res.data
      );


      if (
        res.data.length > 0
        && conversationId === null
      ) {

        setConversationId(
          res.data[0].id
        );

      }

    } catch (error) {

      console.error(
        "Failed to load conversations",
        error
      );

    }

  }


  async function loadMessages(
    id: number
  ) {

    try {

      const res = await api.get(

        `/ai/conversations/${id}/messages`

      );


      setMessages(
        res.data
      );

    } catch (error) {

      console.error(
        "Failed to load messages",
        error
      );

    }

  }


  async function newConversation() {

    if (loading) {
      return;
    }


    const res = await api.post(

      "/ai/conversations",

      {
        provider,
      }

    );


    setMessages([]);


    setConversationId(
      res.data.id
    );


    await loadConversations();

  }

  async function createConversationForMessage() {

    const res = await api.post(

      "/ai/conversations",

      {
        provider,
      }

    );


    const newId =
      res.data.id;


    skipNextMessageLoadRef.current =
      true;


    setConversationId(
      newId
    );


    setConversations(
      (current) => [

        {
          id:
            res.data.id,

          title:
            res.data.title,

          provider:
            res.data.provider,
        },

        ...current,

      ]
    );


    return newId;

  }

  async function deleteConversation(
    id: number
  ) {

    if (loading) {
      return;
    }


    const confirmed =
      window.confirm(
        "Delete this chat permanently?"
      );


    if (!confirmed) {
      return;
    }


    try {

      await api.delete(

        `/ai/conversations/${id}`

      );


      const remainingConversations =
        conversations.filter(

          (conversation) =>
            conversation.id !== id

        );


      setConversations(
        remainingConversations
      );


      if (
        conversationId === id
      ) {

        setMessages([]);


        if (
          remainingConversations.length > 0
        ) {

          setConversationId(

            remainingConversations[0].id

          );

        } else {

          setConversationId(
            null
          );

        }

      }


    } catch (error) {

      console.error(
        "Failed to delete conversation",
        error
      );

    }

  }

  async function loadDocuments() {

    try {

      const res = await api.get(
        "/documents/"
      );

      setDocuments(
        res.data
      );

    } catch (error) {

      console.error(
        "Failed to load documents",
        error
      );

    }

  }


  function toggleDocument(
    documentId: number
  ) {

    setSelectedDocumentIds(
      (current) => {

        if (
          current.includes(
            documentId
          )
        ) {

          return current.filter(
            (id) =>
              id !== documentId
          );

        }

        return [
          ...current,
          documentId,
        ];

      }
    );

  }


  async function sendMessage() {

    const cleanQuestion =
      question.trim();


    if (
      !cleanQuestion ||
      loading
    ) {

      return;

    }


    let activeConversationId =
      conversationId;


    if (!activeConversationId) {

      try {

        activeConversationId =
          await createConversationForMessage();


      } catch (error) {

        console.error(
          "Failed to create conversation",
          error
        );


        return;

      }

    }


    const userMessage: Message = {

      role: "user",

      content:
        cleanQuestion,

    };


    setMessages(
      (prev) => [

        ...prev,

        userMessage,

      ]
    );


    setQuestion("");

    setLoading(true);


    const assistantIndex =
      messages.length + 1;


    setMessages(
      (prev) => [

        ...prev,

        {

          role:
            "assistant",

          content: "",

        },

      ]
    );


    try {

      const token =
        localStorage.getItem(
          "token"
        );


      const response =
        await fetch(

          "http://127.0.0.1:8000/ai/stream",

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,

            },

            body:
              JSON.stringify({

                question:
                  cleanQuestion,

                provider,

                conversation_id:
                  activeConversationId,

                document_ids:
                  selectedDocumentIds.length > 0
                    ? selectedDocumentIds
                    : null,

              }),

          }

        );


      if (!response.ok) {

        throw new Error(
          `Request failed with status ${response.status}`
        );

      }


      if (!response.body) {

        throw new Error(
          "Streaming response body is missing."
        );

      }


      const reader =
        response.body.getReader();


      const decoder =
        new TextDecoder();


      let completeAnswer = "";


      while (true) {

        const {
          done,
          value,
        } = await reader.read();


        if (done) {
          break;
        }


        const chunk =
          decoder.decode(

            value,

            {
              stream: true,
            }

          );


        completeAnswer +=
          chunk;


        setMessages(
          (prev) => {

            const updated =
              [...prev];


            updated[
              assistantIndex
            ] = {

              role:
                "assistant",

              content:
                completeAnswer,

            };


            return updated;

          }
        );

      }


      await loadConversations();


    } catch (error) {

      console.error(
        "AI stream failed:",
        error
      );


      setMessages(
        (prev) => {

          const updated =
            [...prev];


          updated[
            assistantIndex
          ] = {

            role:
              "assistant",

            content:
              "Something went wrong while getting the AI response.",

          };


          return updated;

        }
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadConversations();

    loadDocuments();

  }, []);


  useEffect(() => {

    if (!conversationId) {

      return;

    }


    if (
      skipNextMessageLoadRef.current
    ) {

      skipNextMessageLoadRef.current =
        false;

      return;

    }


    loadMessages(
      conversationId
    );

  }, [
    conversationId
  ]);


  useEffect(() => {

    bottomRef.current
      ?.scrollIntoView({

        behavior: "smooth",

      });

  }, [
    messages,
    loading,
  ]);


  return (

    <div
      className="
        grid
        grid-cols-[260px_1fr]
        gap-6
        h-[calc(100vh-80px)]
      "
    >


      <aside
        className="
          border
          rounded-xl
          p-4
          overflow-y-auto
        "
      >


        <button

          onClick={
            newConversation
          }

          disabled={
            loading
          }

          className="
            w-full
            border
            rounded-lg
            px-4
            py-2
            mb-4
            disabled:opacity-50
          "
        >

          + New Chat

        </button>


        <div
          className="
            space-y-2
          "
        >

          {
            conversations.map(
              (conversation) => (

                <div

                  key={
                    conversation.id
                  }

                  className={`
          flex
          items-center
          gap-2
          p-2
          rounded-lg
          border

          ${conversationId
                      === conversation.id

                      ? "bg-gray-100"

                      : ""
                    }
        `}
                >


                  <button

                    disabled={
                      loading
                    }

                    onClick={() =>

                      setConversationId(
                        conversation.id
                      )

                    }

                    className="
            flex-1
            min-w-0
            text-left
            p-1
            disabled:opacity-50
          "
                  >


                    <div
                      className="
              font-medium
              truncate
            "
                    >

                      {
                        conversation.title
                      }

                    </div>


                    <div
                      className="
              text-xs
              text-gray-500
              mt-1
            "
                    >

                      {
                        conversation.provider
                      }

                    </div>

                  </button>


                  <button

                    type="button"

                    disabled={
                      loading
                    }

                    onClick={() =>
                      deleteConversation(
                        conversation.id
                      )
                    }

                    title="Delete chat"

                    className="
            shrink-0
            w-8
            h-8
            flex
            items-center
            justify-center
            rounded-md
            text-gray-500
            hover:bg-red-50
            hover:text-red-600
            disabled:opacity-50
          "
                  >

                    ×

                  </button>

                </div>

              )
            )
          }

        </div>

      </aside>


      <main
        className="
          flex
          flex-col
          min-w-0
        "
      >


        <div
          className="
            flex
            items-center
            justify-between
            mb-4
          "
        >


          <div>

            <h1
              className="
                text-3xl
                font-bold
              "
            >

              German AI Tutor

            </h1>


            <p
              className="
                text-gray-500
              "
            >

              Context-aware German learning assistant

            </p>

          </div>


          <select

            value={
              provider
            }

            disabled={
              loading
            }

            onChange={(e) =>

              setProvider(
                e.target.value
              )

            }

            className="
              border
              rounded-lg
              p-2
              disabled:opacity-50
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


        {
          documents.length > 0 && (

            <div
              className="
                  border
                  rounded-xl
                  p-4
                  mb-4
                "
            >

              <div
                className="
                    font-medium
                    mb-3
                  "
              >

                Use documents as context

              </div>


              <div
                className="
                    flex
                    flex-wrap
                    gap-2
                  "
              >

                {
                  documents.map(
                    (document) => {

                      const selected =
                        selectedDocumentIds.includes(
                          document.id
                        );


                      return (

                        <button

                          key={
                            document.id
                          }

                          onClick={() =>
                            toggleDocument(
                              document.id
                            )
                          }

                          disabled={
                            loading
                            || document.status !== "processed"
                          }

                          className={`
                              border
                              rounded-lg
                              px-3
                              py-2
                              text-sm
                              disabled:opacity-50

                              ${selected
                              ? "bg-gray-900 text-white"
                              : ""
                            }
                            `}
                        >

                          {
                            document.filename
                          }

                        </button>

                      );

                    }
                  )
                }

              </div>


              {
                selectedDocumentIds.length > 0 && (

                  <div
                    className="
                        text-sm
                        text-gray-500
                        mt-3
                      "
                  >

                    {
                      selectedDocumentIds.length
                    }

                    {" document(s) selected"}

                  </div>

                )
              }

            </div>

          )
        }


        <div
          className="
              border
              rounded-xl
              flex-1
              overflow-y-auto
              p-6
              space-y-6
            "
        >


          {
            messages.length === 0
            && !loading
            && (

              <div
                className="
                  h-full
                  flex
                  items-center
                  justify-center
                  text-gray-400
                "
              >

                Start a conversation

              </div>

            )
          }


          {
            messages.map(
              (msg, index) => (

                <ChatBubble

                  key={
                    msg.id
                    ?? index
                  }

                  role={
                    msg.role
                  }

                  content={
                    msg.content
                    || "..."
                  }

                />

              )
            )
          }


          <div
            ref={
              bottomRef
            }
          />

        </div>


        <div
          className="
            flex
            gap-3
            mt-4
          "
        >


          <input

            value={
              question
            }

            disabled={
              loading
            }

            onChange={(e) =>

              setQuestion(
                e.target.value
              )

            }

            onKeyDown={(e) => {

              if (
                e.key === "Enter"
                && !e.shiftKey
              ) {

                sendMessage();

              }

            }}

            placeholder="Ask your German question..."

            className="
              border
              rounded-lg
              px-4
              py-3
              flex-1
              disabled:opacity-50
            "
          />


          <button

            onClick={
              sendMessage
            }

            disabled={
              loading
              || !question.trim()
            }

            className="
              border
              rounded-lg
              px-6
              py-3
              disabled:opacity-50
            "
          >

            {
              loading
                ? "Generating..."
                : "Send"
            }

          </button>

        </div>

      </main>

    </div>

  );
}