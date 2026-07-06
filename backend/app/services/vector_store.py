import chromadb

from app.services.embedding_service import (
    EmbeddingService,
)


class VectorStore:


    def __init__(self):

        self.client = (
            chromadb.PersistentClient(
                path="chroma_db"
            )
        )


        self.collection = (
            self.client
            .get_or_create_collection(
                name="german_documents"
            )
        )


        self.embedding_service = (
            EmbeddingService()
        )


    def add_document_chunks(

        self,

        user_id: int,

        document_id: int,

        filename: str,

        chunks: list[str],

    ):

        if not chunks:

            return


        embeddings = (

            self.embedding_service
            .embed_documents(
                chunks
            )

        )


        ids = []

        metadatas = []


        for index in range(
            len(chunks)
        ):

            ids.append(

                f"user_{user_id}_document_{document_id}_chunk_{index}"

            )


            metadatas.append({

                "user_id":
                    user_id,

                "document_id":
                    document_id,

                "filename":
                    filename,

                "chunk_index":
                    index,

            })


        self.collection.add(

            ids=ids,

            documents=chunks,

            embeddings=
                embeddings.tolist(),

            metadatas=
                metadatas,

        )


    def search(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

    ):

        embedding = (

            self.embedding_service
            .embed_text(
                query
            )

        )


        where_filter = {

            "user_id":
                user_id

        }


        if document_ids:

            where_filter = {

                "$and": [

                    {
                        "user_id":
                            user_id
                    },

                    {
                        "document_id": {

                            "$in":
                                document_ids

                        }
                    },

                ]

            }


        results = (

            self.collection.query(

                query_embeddings=[

                    embedding.tolist()

                ],

                n_results=top_k,

                where=where_filter,

            )

        )


        return results


    def delete_document(

        self,

        user_id: int,

        document_id: int,

    ):

        self.collection.delete(

            where={

                "$and": [

                    {
                        "user_id":
                            user_id
                    },

                    {
                        "document_id":
                            document_id
                    },

                ]

            }

        )