import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Flashcards() {

  const [cards, setCards] =
    useState<any[]>([]);

  const [current, setCurrent] =
    useState(0);

  const [showAnswer, setShowAnswer] =
    useState(false);

  async function loadCards() {

    const res = await api.get(
      "/flashcards/due"
    );

    setCards(res.data);
  }

  async function review(
    rating: string
  ) {

    const card =
      cards[current];

    await api.post(
      `/flashcards/review/${card.flashcard_id}`,
      {
        rating
      }
    );

    setShowAnswer(false);

    if (
      current <
      cards.length - 1
    ) {

      setCurrent(
        current + 1
      );

    } else {

      loadCards();
      setCurrent(0);

    }
  }

  useEffect(() => {
    loadCards();
  }, []);

  if (
    cards.length === 0
  ) {
    return (
      <div className="p-8">

        <h1
          className="
            text-3xl
            font-bold
          "
        >
          Flashcards
        </h1>

        <div className="mt-6">
          No reviews due.
        </div>

      </div>
    );
  }

  const card =
    cards[current];

  return (
    <div className="p-8">

      <h1
        className="
          text-3xl
          font-bold
          mb-8
        "
      >
        Flashcards
      </h1>

      <div
        className="
          border
          rounded-xl
          p-10
          text-center
        "
      >

        <div
          className="
            text-4xl
            font-bold
          "
        >
          {card.word}
        </div>

        {
          showAnswer && (

            <div
              className="
                mt-6
                text-xl
              "
            >
              {card.translation}
            </div>

          )
        }

      </div>

      {
        !showAnswer ? (

          <button
            onClick={() =>
              setShowAnswer(true)
            }
            className="
              mt-6
              border
              px-4
              py-2
              rounded
            "
          >
            Show Answer
          </button>

        ) : (

          <div
            className="
              flex
              gap-3
              mt-6
            "
          >

            <button
              onClick={() =>
                review("again")
              }
              className="
                border
                px-4
                py-2
                rounded
              "
            >
              Again
            </button>

            <button
              onClick={() =>
                review("hard")
              }
              className="
                border
                px-4
                py-2
                rounded
              "
            >
              Hard
            </button>

            <button
              onClick={() =>
                review("good")
              }
              className="
                border
                px-4
                py-2
                rounded
              "
            >
              Good
            </button>

            <button
              onClick={() =>
                review("easy")
              }
              className="
                border
                px-4
                py-2
                rounded
              "
            >
              Easy
            </button>

          </div>

        )
      }

    </div>
  );
}