import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Planner() {

  const [plan, setPlan] =
    useState<any>(null);

  async function loadPlan() {

    const res = await api.get(
      "/planner/today"
    );

    setPlan(res.data);
  }

  useEffect(() => {
    loadPlan();
  }, []);

  if (!plan) {
    return (
      <div className="p-8">
        Loading...
      </div>
    );
  }

  return (
    <div className="p-8">

      <h1
        className="
          text-4xl
          font-bold
          mb-8
        "
      >
        Today's Study Plan
      </h1>

      <div
        className="
          border
          rounded-xl
          p-6
          mb-6
        "
      >

        <h2
          className="
            text-2xl
            font-bold
            mb-4
          "
        >
          Weak Vocabulary
        </h2>

        {
          plan.weak_words?.length > 0
          ? (
            <div className="space-y-3">

              {
                plan.weak_words.map(
                  (word: any) => (

                    <div
                      key={word.word}
                      className="
                        border
                        rounded-lg
                        p-3
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
                        Mastery:
                        {" "}
                        {word.mastery}
                        %
                      </div>

                    </div>

                  )
                )
              }

            </div>
          )
          : (
            <div>
              No vocabulary data yet.
            </div>
          )
        }

      </div>

      <div
        className="
          border
          rounded-xl
          p-6
          mb-6
        "
      >

        <h2
          className="
            text-2xl
            font-bold
            mb-4
          "
        >
          Weak Grammar Topic
        </h2>

        {
          plan.weak_topic ? (

            <>

              <div>

                Topic:

                {" "}

                {plan.weak_topic.name}

              </div>

              <div>

                Mastery:

                {" "}

                {plan.weak_topic.mastery}
                %

              </div>

            </>

          ) : (

            <div>
              No grammar data yet.
            </div>

          )
        }

      </div>

      <div
        className="
          border
          rounded-xl
          p-6
        "
      >

        <h2
          className="
            text-2xl
            font-bold
            mb-4
          "
        >
          Recommended Actions
        </h2>

        <ul className="space-y-2">

          <li>
            📚 Review
            {" "}
            {plan.recommended_flashcards}
            {" "}
            weak words
          </li>

          <li>
            🆕 Learn
            {" "}
            {plan.recommended_new_words}
            {" "}
            new words
          </li>

          <li>
            ✍️ Complete
            {" "}
            {plan.recommended_grammar}
            {" "}
            grammar exercises
          </li>

        </ul>

      </div>

    </div>
  );
}