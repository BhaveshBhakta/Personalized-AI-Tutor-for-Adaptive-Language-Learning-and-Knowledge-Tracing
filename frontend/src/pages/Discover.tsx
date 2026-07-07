import { useEffect } from "react";
import { useState } from "react";

import { api } from "../api/client";

import type { GermanWord }
  from "../types/germanWord";

export default function Discover() {

  const [words, setWords] =
    useState<GermanWord[]>([]);

  const [loading, setLoading] =
    useState(true);

  async function loadWords() {

    try {

      const res =
        await api.get(
          "/german-words/"
        );

      setWords(res.data);

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);

    }

  }

  async function addWord(
    wordId: number
  ) {

    try {

      await api.post(
        `/german-words/${wordId}/add`,
        {}
      );

      alert(
        "Added to vocabulary"
      );

    } catch (err) {

      console.error(err);

      alert(
        "Unable to add word"
      );

    }

  }

  useEffect(() => {

    loadWords();

  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>

      <h1
        className="
          text-3xl
          font-bold
          mb-8
        "
      >
        Discover Words
      </h1>

      <div
        className="
          grid
          gap-4
        "
      >

        {words.map((word) => (

          <div
            key={word.id}
            className="
              border
              rounded-lg
              p-4
            "
          >

            <div
              className="
                text-xl
                font-bold
              "
            >
              {word.article}
              {" "}
              {word.word}
            </div>

            <div>
              {word.translation}
            </div>

            <div
              className="
                text-sm
                text-gray-500
                mt-1
              "
            >
              {word.category}
            </div>

            <button
              onClick={() =>
                addWord(word.id)
              }
              className="
                mt-4
                border
                px-3
                py-1
              "
            >
              Add
            </button>

          </div>

        ))}

      </div>

    </div>
  );
}