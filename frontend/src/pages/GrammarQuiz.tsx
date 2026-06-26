import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function GrammarQuiz() {
  const [questions, setQuestions] =
    useState<any[]>([]);

  const [current, setCurrent] =
    useState(0);

  const [result, setResult] =
    useState<any>(null);

  const [score, setScore] =
    useState(0);

  const [answered, setAnswered] =
    useState(false);

  async function loadQuestions() {
    const res = await api.get(
      "/grammar/topic/1/questions"
    );

    setQuestions(res.data);
  }

  async function answer(
    selected: string
  ) {
    const question =
      questions[current];

    const res =
      await api.post(
        `/grammar/question/${question.id}/answer`,
        null,
        {
          params: {
            answer: selected,
          },
        }
      );

    setResult(res.data);

    setAnswered(true);

    if (res.data.correct) {
      setScore(
        (prev) => prev + 1
      );
    }
  }

  function nextQuestion() {
    setResult(null);

    setAnswered(false);

    if (
      current <
      questions.length - 1
    ) {
      setCurrent(
        current + 1
      );
    } else {
      setCurrent(
        questions.length
      );
    }
  }

  useEffect(() => {
    loadQuestions();
  }, []);

  if (
    questions.length === 0
  ) {
    return (
      <div className="p-8">
        Loading...
      </div>
    );
  }

  if (
    current >= questions.length
  ) {
    return (
      <div className="p-8">

        <h1
          className="
            text-4xl
            font-bold
          "
        >
          Session Complete 🎉
        </h1>

        <div
          className="
            mt-6
            text-xl
          "
        >
          Score:
          {" "}
          {score}
          /
          {questions.length}
        </div>

      </div>
    );
  }

  const question =
    questions[current];

  return (
    <div className="p-8">

      <h1
        className="
          text-3xl
          font-bold
          mb-8
        "
      >
        Grammar Quiz
      </h1>

      <div
        className="
          border
          p-6
          rounded-lg
        "
      >

        <div
          className="
            text-sm
            mb-4
          "
        >
          Question
          {" "}
          {current + 1}
          {" / "}
          {questions.length}
        </div>

        <div
          className="
            text-2xl
            mb-6
          "
        >
          {question.question}
        </div>

        <button
          disabled={answered}
          onClick={() =>
            answer(
              question.option_a
            )
          }
          className="
            border
            px-4
            py-2
            rounded
            mr-2
          "
        >
          {question.option_a}
        </button>

        <button
          disabled={answered}
          onClick={() =>
            answer(
              question.option_b
            )
          }
          className="
            border
            px-4
            py-2
            rounded
            mr-2
          "
        >
          {question.option_b}
        </button>

        <button
          disabled={answered}
          onClick={() =>
            answer(
              question.option_c
            )
          }
          className="
            border
            px-4
            py-2
            rounded
          "
        >
          {question.option_c}
        </button>

      </div>

      {result && (

        <div className="mt-6">

          <div>
            {result.correct
              ? "Correct ✅"
              : `Wrong ❌ | Correct Answer: ${result.expected}`}
          </div>

          <div className="mt-2">
            Mastery:
            {" "}
            {result.mastery}
            %
          </div>

          <button
            onClick={nextQuestion}
            className="
              mt-4
              border
              px-4
              py-2
              rounded
            "
          >
            Next Question
          </button>

        </div>

      )}

    </div>
  );
}