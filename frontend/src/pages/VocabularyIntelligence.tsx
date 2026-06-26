import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function VocabularyIntelligence() {

  const [words, setWords] =
    useState<any[]>([]);

  async function loadWords() {

    const res =
      await api.get(
        "/vocabulary-intelligence/weak-words"
      );

    setWords(res.data);
  }

  useEffect(() => {
    loadWords();
  }, []);

  return (
    <div className="p-8">

      <h1
        className="
          text-3xl
          font-bold
          mb-6
        "
      >
        Weak Vocabulary
      </h1>

      <div className="space-y-3">

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
                font-semibold
              "
            >
              {word.word}
            </div>

            <div>
              {word.translation}
            </div>

            <div>
              Mastery:
              {" "}
              {word.mastery}
              %
            </div>

          </div>

        ))}

      </div>

    </div>
  );
}