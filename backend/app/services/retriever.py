from app.services.vector_store import (
    VectorStore,
)


class Retriever:

    def __init__(self):

        self.vector_store = (
            VectorStore()
        )

    def retrieve_context(

        self,

        query: str,

        top_k: int = 5,

    ) -> str:

        results = (
            self.vector_store.search(
                query=query,
                top_k=top_k,
            )
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        context = "\n\n".join(
            documents
        )

        return context