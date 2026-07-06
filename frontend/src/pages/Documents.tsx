import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  api,
} from "../api/client";


interface DocumentItem {

  id: number;

  filename: string;

  status: string;

  uploaded_at: string;

}


export default function Documents() {


  const [
    documents,
    setDocuments,
  ] = useState<DocumentItem[]>([]);


  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(
    null
  );


  const [
    uploading,
    setUploading,
  ] = useState(false);


  const [
    message,
    setMessage,
  ] = useState("");


  const inputRef =
    useRef<HTMLInputElement | null>(
      null
    );


  async function loadDocuments() {

    const res = await api.get(
      "/documents/"
    );


    setDocuments(
      res.data
    );

  }


  async function uploadDocument() {

    if (!selectedFile) {

      setMessage(
        "Select a PDF first."
      );

      return;

    }


    const formData =
      new FormData();


    formData.append(
      "file",
      selectedFile
    );


    setUploading(true);

    setMessage("");


    try {

      const res = await api.post(

        "/documents/upload",

        formData,

        {

          headers: {

            "Content-Type":
              "multipart/form-data",

          },

        }

      );


      setMessage(

        `${res.data.filename} processed successfully. ${res.data.chunks} chunks created.`

      );


      setSelectedFile(null);


      if (inputRef.current) {

        inputRef.current.value = "";

      }


      await loadDocuments();


    } catch (error: any) {

      setMessage(

        error.response?.data?.detail
        ?? "Upload failed."

      );


    } finally {

      setUploading(false);

    }

  }


  async function deleteDocument(
    id: number
  ) {

    const confirmed =
      window.confirm(
        "Delete this document?"
      );


    if (!confirmed) {

      return;

    }


    await api.delete(

      `/documents/${id}`

    );


    await loadDocuments();

  }


  useEffect(() => {

    loadDocuments();

  }, []);


  return (

    <div
      className="
        max-w-5xl
        mx-auto
      "
    >


      <div
        className="
          mb-8
        "
      >

        <h1
          className="
            text-4xl
            font-bold
          "
        >

          Documents

        </h1>


        <p
          className="
            text-gray-500
            mt-2
          "
        >

          Upload German learning material and use it with the AI Tutor.

        </p>

      </div>


      <div
        className="
          border
          rounded-xl
          p-6
          mb-8
        "
      >

        <h2
          className="
            text-xl
            font-semibold
            mb-4
          "
        >

          Upload PDF

        </h2>


        <div
          className="
            flex
            gap-4
            items-center
          "
        >

          <input

            ref={
              inputRef
            }

            type="file"

            accept=".pdf,application/pdf"

            onChange={(event) =>

              setSelectedFile(

                event.target.files?.[0]
                ?? null

              )

            }

            className="
              border
              rounded-lg
              p-3
              flex-1
            "
          />


          <button

            onClick={
              uploadDocument
            }

            disabled={
              uploading
              || !selectedFile
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
              uploading
                ? "Processing..."
                : "Upload"
            }

          </button>

        </div>


        {
          message && (

            <div
              className="
                mt-4
                text-sm
              "
            >

              {message}

            </div>

          )
        }

      </div>


      <div
        className="
          border
          rounded-xl
          overflow-hidden
        "
      >

        <div
          className="
            p-5
            border-b
          "
        >

          <h2
            className="
              text-xl
              font-semibold
            "
          >

            Document Library

          </h2>

        </div>


        {
          documents.length === 0 ? (

            <div
              className="
                p-8
                text-center
                text-gray-500
              "
            >

              No documents uploaded yet.

            </div>

          ) : (

            <div>

              {
                documents.map(
                  (document) => (

                    <div

                      key={
                        document.id
                      }

                      className="
                        flex
                        items-center
                        justify-between
                        p-5
                        border-b
                        last:border-b-0
                      "
                    >

                      <div>

                        <div
                          className="
                            font-medium
                          "
                        >

                          {
                            document.filename
                          }

                        </div>


                        <div
                          className="
                            text-sm
                            text-gray-500
                            mt-1
                          "
                        >

                          {
                            document.status
                          }

                          {" · "}

                          {
                            new Date(
                              document.uploaded_at
                            ).toLocaleString()
                          }

                        </div>

                      </div>


                      <button

                        onClick={() =>
                          deleteDocument(
                            document.id
                          )
                        }

                        className="
                          border
                          rounded-lg
                          px-4
                          py-2
                        "
                      >

                        Delete

                      </button>

                    </div>

                  )
                )
              }

            </div>

          )
        }

      </div>

    </div>

  );
}