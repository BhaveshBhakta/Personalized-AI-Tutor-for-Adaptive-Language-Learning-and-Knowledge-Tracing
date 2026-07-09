import logging

from app.services.vector_store import (
    VectorStore,
)

logger = logging.getLogger(
    __name__
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

        max_distance:
            float | None = None,

        max_context_chars:
            int = 12000,

    ) -> str:

        retrieval = (
            self.retrieve_with_sources(

                query=query,

                user_id=user_id,

                document_ids=
                    document_ids,

                top_k=top_k,

                max_distance=
                    max_distance,

                max_context_chars=
                    max_context_chars,

            )
        )


        return retrieval[
            "context"
        ]


    def _normalize_text(

        self,

        text: str,

    ) -> str:

        return " ".join(

            text
            .lower()
            .split()

        )


    def _word_set(

        self,

        text: str,

    ) -> set[str]:

        normalized = (
            self._normalize_text(
                text
            )
        )


        return set(
            normalized.split()
        )


    def _overlap_ratio(

        self,

        text_a: str,

        text_b: str,

    ) -> float:

        words_a = (
            self._word_set(
                text_a
            )
        )


        words_b = (
            self._word_set(
                text_b
            )
        )


        if (
            not words_a
            or not words_b
        ):

            return 0.0


        intersection = (
            words_a.intersection(
                words_b
            )
        )


        smaller_size = min(

            len(words_a),

            len(words_b),

        )


        if smaller_size == 0:

            return 0.0


        return (

            len(intersection)
            / smaller_size

        )


    def _is_duplicate(

        self,

        candidate_text: str,

        selected_sources:
            list[dict],

        overlap_threshold:
            float = 0.85,

    ) -> bool:

        candidate_normalized = (
            self._normalize_text(
                candidate_text
            )
        )


        for source in selected_sources:

            existing_text = (
                source.get(
                    "text",
                    ""
                )
            )


            existing_normalized = (
                self._normalize_text(
                    existing_text
                )
            )


            if (
                candidate_normalized
                == existing_normalized
            ):

                return True


            overlap = (
                self._overlap_ratio(

                    candidate_text,

                    existing_text,

                )
            )


            if (
                overlap
                >= overlap_threshold
            ):

                return True


        return False


    def retrieve_with_sources(

        self,

        query: str,

        user_id: int,

        document_ids:
            list[int] | None = None,

        top_k: int = 5,

        max_distance:
            float | None = None,

        max_context_chars:
            int = 12000,

        max_chunks_per_document:
            int = 3,

        overlap_threshold:
            float = 0.85,

    ) -> dict:


        selected_document_count = (

            len(document_ids)

            if document_ids

            else 1

        )


        candidate_k = max(

            top_k * 3,

            selected_document_count * 4,

        )


        results = (
            self.vector_store.search(

                query=query,

                user_id=user_id,

                document_ids=
                    document_ids,

                top_k=
                    candidate_k,

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


        candidates = []


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


            normalized_distance = (

                float(distance)

                if distance is not None

                else None

            )


            if (

                max_distance
                is not None

                and normalized_distance
                is not None

                and normalized_distance
                > max_distance

            ):

                continue


            candidate = {

                "document_id":
                    metadata.get(
                        "document_id"
                    ),

                "filename":
                    metadata.get(

                        "filename",

                        "Unknown document",

                    ),

                "chunk_index":
                    metadata.get(
                        "chunk_index"
                    ),

                "text":
                    text,

            }


            if (
                normalized_distance
                is not None
            ):

                candidate[
                    "distance"
                ] = (
                    normalized_distance
                )


            candidates.append(
                candidate
            )


        # Chroma normally returns results
        # ordered by distance, but sorting
        # explicitly makes the Retriever's
        # ranking behavior clear.

        candidates.sort(

            key=lambda source: (

                source.get(
                    "distance",
                    float("inf"),
                )

            )

        )


        deduplicated = []


        for candidate in candidates:

            duplicate = (
                self._is_duplicate(

                    candidate_text=
                        candidate["text"],

                    selected_sources=
                        deduplicated,

                    overlap_threshold=
                        overlap_threshold,

                )
            )


            if duplicate:

                continue


            deduplicated.append(
                candidate
            )


        selected_sources = []

        selected_keys = set()

        document_counts = {}


        # First balancing pass:
        # give each selected document a chance
        # to contribute its best retrieved chunk.
        #
        # This does NOT invent or force a chunk.
        # A document contributes only if it has
        # a candidate in the retrieval results.

        if (
            document_ids
            and len(document_ids) > 1
        ):

            for document_id in document_ids:

                for candidate in deduplicated:

                    if (

                        candidate[
                            "document_id"
                        ]
                        != document_id

                    ):

                        continue


                    key = (

                        candidate[
                            "document_id"
                        ],

                        candidate[
                            "chunk_index"
                        ],

                    )


                    if key in selected_keys:

                        continue


                    selected_sources.append(
                        candidate
                    )


                    selected_keys.add(
                        key
                    )


                    document_counts[
                        document_id
                    ] = (

                        document_counts.get(
                            document_id,
                            0,
                        )
                        + 1

                    )


                    break


                    # Only the best candidate
                    # from this document is added
                    # during the balancing pass.


                    # The next pass can add more
                    # chunks from this document.


        # Ranking pass:
        # fill remaining slots using semantic
        # ranking while respecting the soft
        # per-document cap.

        for candidate in deduplicated:

            if (
                len(selected_sources)
                >= top_k
            ):

                break


            key = (

                candidate[
                    "document_id"
                ],

                candidate[
                    "chunk_index"
                ],

            )


            if key in selected_keys:

                continue


            document_id = (
                candidate[
                    "document_id"
                ]
            )


            current_count = (
                document_counts.get(
                    document_id,
                    0,
                )
            )


            if (
                current_count
                >= max_chunks_per_document
            ):

                continue


            selected_sources.append(
                candidate
            )


            selected_keys.add(
                key
            )


            document_counts[
                document_id
            ] = (

                current_count
                + 1

            )


        # The balancing pass can exceed top_k
        # if the user selected more documents
        # than the requested final result count.
        #
        # Keep the strongest final top_k results.

        selected_sources.sort(

            key=lambda source: (

                source.get(
                    "distance",
                    float("inf"),
                )

            )

        )


        selected_sources = (
            selected_sources[
                :top_k
            ]
        )


        context_parts = []

        final_sources = []

        current_context_chars = 0

        source_number = 1


        for source in selected_sources:

            source_block = (

                f"[SOURCE {source_number}]\n"

                f"Filename: "
                f"{source['filename']}\n"

                f"Document ID: "
                f"{source['document_id']}\n"

                f"Chunk: "
                f"{source['chunk_index']}\n\n"

                f"{source['text']}\n"

                f"[END SOURCE "
                f"{source_number}]"

            )


            projected_size = (

                current_context_chars

                + len(source_block)

                + 2

            )


            if (

                projected_size
                > max_context_chars

                and context_parts

            ):

                break


            context_parts.append(
                source_block
            )


            final_sources.append(
                source
            )


            current_context_chars = (
                projected_size
            )


            source_number += 1


        context = "\n\n".join(
            context_parts
        )


        best_distance = (

            min(

                (
                    source["distance"]

                    for source
                    in final_sources

                    if source.get(
                        "distance"
                    )
                    is not None
                ),

                default=None,

            )

        )

        print("\n========== RAG DISTANCE TEST ==========")

        print(
            "Question:",
            query,
        )

        print(
            "Best distance:",
            best_distance,
        )

        print(
            "All distances:",
            [
                source.get("distance")
                for source in final_sources
            ],
        )

        print(
            "Sources:",
            [
                {
                    "filename":
                        source["filename"],

                    "chunk_index":
                        source["chunk_index"],
                }

                for source in final_sources
            ],
        )

        print("=======================================\n")

        logger.debug(

            (
                "RAG retrieval | "
                "query=%r | "
                "documents=%s | "
                "raw=%d | "
                "deduplicated=%d | "
                "final=%d | "
                "best_distance=%s | "
                "context_chars=%d"
            ),

            query,

            document_ids,

            len(candidates),

            len(deduplicated),

            len(final_sources),

            best_distance,

            len(context),

        )


        return {

            "context":
                context,

            "sources":
                final_sources,

            "has_evidence":
                len(final_sources) > 0,

            "best_distance":
                best_distance,

            "retrieval_debug": {

                "candidate_k":
                    candidate_k,

                "raw_candidates":
                    len(candidates),

                "after_deduplication":
                    len(deduplicated),

                "final_sources":
                    len(final_sources),

                "context_chars":
                    len(context),

                "best_distance":
                    best_distance,

            },

        }