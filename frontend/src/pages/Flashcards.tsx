import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Flashcard {
  flashcard_id: number;
  word: string;
  translation: string;
  mastery: number;
  stability: number;
  difficulty: number;
  retrievability: number;
  interval_days: number;
}

export default function Flashcards() {

  const [cards, setCards] =
    useState<Flashcard[]>([]);

  const [current, setCurrent] =
    useState(0);

  const [showAnswer, setShowAnswer] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [xp, setXP] =
    useState(0);

  async function loadCards() {

    const token =
      localStorage.getItem("token");

    const res = await api.get(
      "/flashcards/due",
      {
        headers: {
          Authorization:
            `Bearer ${token}`,
        },
      }
    );

    setCards(res.data);

    setLoading(false);
  }

  async function review(
    rating: string
  ) {

    const token =
      localStorage.getItem("token");

    const card =
      cards[current];

    const res =
      await api.post(
        `/flashcards/review/${card.flashcard_id}`,
        {
          rating,
        },
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

    setXP(res.data.xp);

    if (
      current <
      cards.length - 1
    ) {

      setCurrent(
        current + 1
      );

      setShowAnswer(false);

    } else {

      loadCards();

      setCurrent(0);

      setShowAnswer(false);

    }
  }

  useEffect(() => {
    loadCards();
  }, []);

  if (loading)
    return (
      <div className="p-8">
        Loading...
      </div>
    );

  if (cards.length === 0)
    return (
      <div className="p-8">

        <h1 className="text-4xl font-bold">
          Flashcards
        </h1>

        <div className="mt-8">

          🎉 No reviews due today.

        </div>

      </div>
    );

  const card =
    cards[current];

  return (

    <div className="p-8 max-w-3xl mx-auto">

      <h1
        className="
          text-4xl
          font-bold
          mb-8
        "
      >
        Flashcards
      </h1>

      <div
        className="
          mb-6
          text-gray-500
        "
      >

        Progress

        {" "}

        {current + 1}

        /

        {cards.length}

      </div>

      <div
        className="
          border
          rounded-xl
          p-12
          text-center
          shadow
        "
      >

        <div
          className="
            text-5xl
            font-bold
          "
        >
          {card.word}
        </div>

        {

          showAnswer && (

            <>

              <div
                className="
                  mt-8
                  text-3xl
                "
              >
                {card.translation}
              </div>

              <div
                className="
                  mt-10
                  space-y-2
                  text-gray-500
                "
              >

                <div>

                  Mastery

                  {" "}

                  {card.mastery}%

                </div>

                <div>

                  Retention

                  {" "}

                  {Math.round(
                    card.retrievability * 100
                  )}%

                </div>

                <div>

                  Next Review

                  {" "}

                  {card.interval_days}

                  {" "}

                  day(s)

                </div>

              </div>

            </>

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
              mt-8
              w-full
              border
              rounded-lg
              py-3
            "

          >

            Show Answer

          </button>

        ) : (

          <div
            className="
              grid
              grid-cols-4
              gap-3
              mt-8
            "
          >

            <button
              onClick={() =>
                review("again")
              }
              className="border py-3 rounded-lg"
            >
              Again
            </button>

            <button
              onClick={() =>
                review("hard")
              }
              className="border py-3 rounded-lg"
            >
              Hard
            </button>

            <button
              onClick={() =>
                review("good")
              }
              className="border py-3 rounded-lg"
            >
              Good
            </button>

            <button
              onClick={() =>
                review("easy")
              }
              className="border py-3 rounded-lg"
            >
              Easy
            </button>

          </div>

        )

      }

      <div
        className="
          mt-10
          text-center
          text-xl
        "
      >

        XP

        {" "}

        {xp}

      </div>

    </div>

  );

}