import chromadb

from app.services.embedding_service import (
    EmbeddingService,
)


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="german_documents"
            )
        )

        self.embedding_service = (
            EmbeddingService()
        )

    def add_document_chunks(

        self,

        document_id: int,

        chunks: list[str],

    ):

        embeddings = (
            self.embedding_service.embed_documents(
                chunks
            )
        )

        ids = []

        metadatas = []

        for i in range(len(chunks)):

            ids.append(
                f"{document_id}_{i}"
            )

            metadatas.append({

                "document_id":
                document_id,

                "chunk_index":
                i,

            })

        self.collection.add(

            ids=ids,

            documents=chunks,

            embeddings=embeddings.tolist(),

            metadatas=metadatas,

        )

    def search(

        self,

        query: str,

        top_k: int = 5,

    ):

        embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        results = self.collection.query(

            query_embeddings=[
                embedding.tolist()
            ],

            n_results=top_k,

        )

        return results