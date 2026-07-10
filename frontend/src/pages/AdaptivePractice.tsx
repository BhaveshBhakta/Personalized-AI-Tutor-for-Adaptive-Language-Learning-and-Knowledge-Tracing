import {
  useState,
} from "react";

import {
  api,
} from "../api/client";


type Exercise = {

  id: number;

  exercise_type: string;

  category: string;

  topic: string;

  difficulty_level: string;

  question: string;

  source_reason: string;

};


type Result = {

  is_correct: boolean;

  score: number;

  feedback: string;

  expected_answer: string;

  explanation: string;

};


export default function AdaptivePractice() {

  const [
    exercises,
    setExercises,
  ] = useState<Exercise[]>([]);


  const [
    currentIndex,
    setCurrentIndex,
  ] = useState(0);


  const [
    answer,
    setAnswer,
  ] = useState("");


  const [
    result,
    setResult,
  ] = useState<Result | null>(
    null
  );


  const [
    loading,
    setLoading,
  ] = useState(false);


  const currentExercise =
    exercises[currentIndex];


  async function startSession() {

    setLoading(true);

    setResult(null);

    setAnswer("");


    try {

      const response =
        await api.post(
          "/exercises/session",
          {
            size: 5,
            provider: "groq",
          }
        );


      setExercises(
        response.data.exercises
      );

      setCurrentIndex(0);


    } catch (error) {

      console.error(
        "Failed to create session",
        error
      );


    } finally {

      setLoading(false);

    }

  }


  async function submitAnswer() {

    if (
      !currentExercise
      || !answer.trim()
    ) {

      return;

    }


    setLoading(true);


    try {

      const response =
        await api.post(

          `/exercises/${currentExercise.id}/submit`,

          {

            answer,

            provider: "groq",

          }

        );


      setResult(
        response.data
      );


    } catch (error) {

      console.error(
        "Failed to submit answer",
        error
      );


    } finally {

      setLoading(false);

    }

  }


  function nextExercise() {

    setAnswer("");

    setResult(null);


    if (
      currentIndex
      < exercises.length - 1
    ) {

      setCurrentIndex(
        currentIndex + 1
      );

    }

  }


  if (!currentExercise) {

    return (

      <div className="max-w-3xl mx-auto">

        <h1 className="text-3xl font-bold mb-3">

          Adaptive Practice

        </h1>


        <p className="mb-6">

          Practice generated from your
          current learning weaknesses.

        </p>


        <button

          onClick={
            startSession
          }

          disabled={
            loading
          }

          className="
            border
            rounded-lg
            px-5
            py-3
          "

        >

          {
            loading
              ? "Preparing practice..."
              : "Start practice session"
          }

        </button>

      </div>

    );

  }


  return (

    <div className="max-w-3xl mx-auto">


      <div className="mb-6">

        Exercise {
          currentIndex + 1
        } of {
          exercises.length
        }

      </div>


      <div
        className="
          border
          rounded-xl
          p-6
        "
      >

        <div className="text-sm mb-3">

          {
            currentExercise.category
          }

          {" · "}

          {
            currentExercise.topic
          }

          {" · "}

          {
            currentExercise.difficulty_level
          }

        </div>


        <h2 className="text-xl font-semibold mb-6">

          {
            currentExercise.question
          }

        </h2>


        <textarea

          value={
            answer
          }

          onChange={
            (event) =>
              setAnswer(
                event.target.value
              )
          }

          disabled={
            Boolean(result)
          }

          className="
            border
            rounded-lg
            p-3
            w-full
            min-h-28
          "

          placeholder="Your answer"

        />


        {
          !result && (

            <button

              onClick={
                submitAnswer
              }

              disabled={
                loading
                || !answer.trim()
              }

              className="
                border
                rounded-lg
                px-5
                py-2
                mt-4
              "

            >

              {
                loading
                  ? "Checking..."
                  : "Submit answer"
              }

            </button>

          )
        }


        {
          result && (

            <div className="mt-6">

              <h3 className="font-semibold">

                {
                  result.is_correct
                    ? "Correct"
                    : "Needs improvement"
                }

              </h3>


              <p className="mt-2">

                Score: {
                  Math.round(
                    result.score * 100
                  )
                }%

              </p>


              <p className="mt-3">

                {
                  result.feedback
                }

              </p>


              {
                !result.is_correct && (

                  <p className="mt-3">

                    Expected answer:{" "}

                    <strong>

                      {
                        result.expected_answer
                      }

                    </strong>

                  </p>

                )
              }


              {
                result.explanation && (

                  <p className="mt-3">

                    {
                      result.explanation
                    }

                  </p>

                )
              }


              <button

                onClick={
                  nextExercise
                }

                className="
                  border
                  rounded-lg
                  px-5
                  py-2
                  mt-5
                "

              >

                Next exercise

              </button>

            </div>

          )
        }

      </div>

    </div>

  );
}