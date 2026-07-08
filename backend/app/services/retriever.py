from app.services.vector_store import (
    VectorStore,
)


class Retriever:


    def __init__(self):

        self.vector_store = (
            VectorStore()
        )


    def retrieve(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

    ) -> str:

        retrieval = (
            self.retrieve_with_sources(

                query=query,

                user_id=user_id,

                document_ids=
                    document_ids,

                top_k=top_k,

            )
        )


        return retrieval[
            "context"
        ]


    def retrieve_with_sources(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

    ) -> dict:

        results = (
            self.vector_store.search(

                query=query,

                user_id=user_id,

                document_ids=
                    document_ids,

                top_k=top_k,

            )
        )


        documents = (
            results.get(
                "documents"
            )
            or [[]]
        )


        metadatas = (
            results.get(
                "metadatas"
            )
            or [[]]
        )


        distances = (
            results.get(
                "distances"
            )
            or [[]]
        )


        document_list = (
            documents[0]
            if documents
            else []
        )


        metadata_list = (
            metadatas[0]
            if metadatas
            else []
        )


        distance_list = (
            distances[0]
            if distances
            else []
        )


        context_parts = []

        sources = []


        for index, text in enumerate(
            document_list
        ):

            metadata = (

                metadata_list[index]

                if index
                < len(metadata_list)

                else {}

            )


            distance = (

                distance_list[index]

                if index
                < len(distance_list)

                else None

            )


            document_id = (
                metadata.get(
                    "document_id"
                )
            )


            filename = (
                metadata.get(
                    "filename",
                    "Unknown document",
                )
            )


            chunk_index = (
                metadata.get(
                    "chunk_index"
                )
            )


            context_parts.append(

                (
                    f"[SOURCE {index + 1}]\n"
                    f"Filename: {filename}\n"
                    f"Document ID: {document_id}\n"
                    f"Chunk: {chunk_index}\n\n"
                    f"{text}\n"
                    f"[END SOURCE {index + 1}]"
                )

            )


            source = {

                "document_id":
                    document_id,

                "filename":
                    filename,

                "chunk_index":
                    chunk_index,

                "text":
                    text,

            }


            if distance is not None:

                source[
                    "distance"
                ] = float(
                    distance
                )


            sources.append(
                source
            )


        context = "\n\n".join(
            context_parts
        )


        return {

            "context":
                context,

            "sources":
                sources,

        }