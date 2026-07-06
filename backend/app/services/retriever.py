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

    ):

        results = (

            self.vector_store.search(

                query=query,

                user_id=user_id,

                document_ids=
                    document_ids,

                top_k=top_k,

            )

        )


        documents = results.get(
            "documents",
            [[]],
        )[0]


        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]


        distances = results.get(
            "distances",
            [[]],
        )[0]


        chunks = []


        for index, content in enumerate(
            documents
        ):

            metadata = (

                metadatas[index]
                if index < len(metadatas)
                else {}

            )


            distance = (

                distances[index]
                if index < len(distances)
                else None

            )


            chunks.append({

                "content":
                    content,

                "document_id":
                    metadata.get(
                        "document_id"
                    ),

                "filename":
                    metadata.get(
                        "filename"
                    ),

                "chunk_index":
                    metadata.get(
                        "chunk_index"
                    ),

                "distance":
                    distance,

            })


        return chunks


    def retrieve_context(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

    ) -> str:

        chunks = self.retrieve(

            query=query,

            user_id=user_id,

            document_ids=
                document_ids,

            top_k=top_k,

        )


        context_parts = []


        for chunk in chunks:

            source = (

                chunk.get("filename")
                or "Unknown document"

            )


            chunk_index = (
                chunk.get(
                    "chunk_index"
                )
            )


            context_parts.append(

                f"""
[SOURCE: {source}]
[CHUNK: {chunk_index}]

{chunk["content"]}
""".strip()

            )


        return "\n\n---\n\n".join(
            context_parts
        )


    def retrieve_with_sources(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

    ):

        chunks = self.retrieve(

            query=query,

            user_id=user_id,

            document_ids=
                document_ids,

            top_k=top_k,

        )


        context_parts = []

        sources = []

        seen_sources = set()


        for chunk in chunks:

            filename = (

                chunk.get("filename")
                or "Unknown document"

            )


            context_parts.append(

                f"""
[SOURCE: {filename}]
[CHUNK: {chunk.get("chunk_index")}]

{chunk["content"]}
""".strip()

            )


            if filename not in seen_sources:

                seen_sources.add(
                    filename
                )

                sources.append({

                    "document_id":
                        chunk.get(
                            "document_id"
                        ),

                    "filename":
                        filename,

                })


        return {

            "context":
                "\n\n---\n\n".join(
                    context_parts
                ),

            "sources":
                sources,

            "chunks":
                chunks,

        }