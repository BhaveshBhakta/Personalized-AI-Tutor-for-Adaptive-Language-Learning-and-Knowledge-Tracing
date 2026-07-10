import {
  useState,
} from "react";

import {
  api,
} from "../api/client";


type ExerciseOption = {
  id: string;
  text: string;
};


type Exercise = {

  exercise_id: string;

  category: string;

  topic: string;

  exercise_type: string;

  difficulty: number;

  question: string;

  options:
    ExerciseOption[] | null;

  hint:
    string | null;

  metadata: {

    mastery_before:
      number;

    confidence:
      number;

  };

};


type AnswerResult = {

  exercise_id: string;

  is_correct: boolean;

  score: number;

  correct_answer: string;

  explanation: string;

  category: string;

  topic: string;

  difficulty: number;

  attempt_number: number;

  grading_method: string;

  next_action: string;

};


export default function AdaptivePractice() {


  const [
    exercise,
    setExercise,
  ] = useState<
    Exercise | null
  >(null);


  const [
    answer,
    setAnswer,
  ] = useState("");


  const [
    result,
    setResult,
  ] = useState<
    AnswerResult | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  async function loadExercise() {


    setLoading(true);

    setError("");

    setAnswer("");

    setResult(null);


    try {


      const response =
        await api.post(
          "/adaptive-exercises/next"
        );


      setExercise(
        response.data
      );


    } catch (error) {


      console.error(
        "Exercise generation failed",
        error
      );


      setError(
        "Could not generate an exercise."
      );


    } finally {


      setLoading(false);


    }

  }


  async function submitAnswer() {


    if (
      !exercise
      || !answer.trim()
    ) {

      return;

    }


    setLoading(true);

    setError("");


    try {


      const response =
        await api.post(

          "/adaptive-exercises/answer",

          {

            exercise_id:
              exercise.exercise_id,

            answer:
              answer,

          }

        );


      setResult(
        response.data
      );


    } catch (error) {


      console.error(
        "Answer submission failed",
        error
      );


      setError(
        "Could not grade the answer."
      );


    } finally {


      setLoading(false);


    }

  }


  return (

    <div
      className="
        max-w-4xl
        mx-auto
        space-y-6
      "
    >


      <div>


        <h1
          className="
            text-3xl
            font-bold
          "
        >
          Adaptive Practice
        </h1>


        <p
          className="
            mt-2
            text-gray-500
          "
        >
          Exercises selected from your
          current learning weaknesses.
        </p>


      </div>


      {!exercise && (

        <button

          onClick={
            loadExercise
          }

          disabled={
            loading
          }

          className="
            border
            rounded-lg
            px-5
            py-3
            disabled:opacity-50
          "

        >

          {
            loading
              ? "Generating..."
              : "Start Practice"
          }

        </button>

      )}


      {error && (

        <div
          className="
            border
            rounded-lg
            p-4
            text-red-500
          "
        >
          {error}
        </div>

      )}


      {exercise && (

        <div
          className="
            border
            rounded-xl
            p-6
            space-y-5
          "
        >


          <div
            className="
              flex
              gap-3
              flex-wrap
              text-sm
            "
          >


            <span
              className="
                border
                rounded-full
                px-3
                py-1
              "
            >
              {exercise.category}
            </span>


            <span
              className="
                border
                rounded-full
                px-3
                py-1
              "
            >
              {exercise.topic}
            </span>


            <span
              className="
                border
                rounded-full
                px-3
                py-1
              "
            >
              Difficulty {
                exercise.difficulty
              }/5
            </span>


          </div>


          <h2
            className="
              text-xl
              font-semibold
            "
          >
            {exercise.question}
          </h2>


          {
            exercise.options

            ? (

              <div
                className="
                  grid
                  gap-3
                "
              >

                {
                  exercise.options.map(
                    (option) => (

                      <button

                        key={
                          option.id
                        }

                        onClick={() =>
                          setAnswer(
                            option.id
                          )
                        }

                        disabled={
                          result !== null
                        }

                        className={`
                          border
                          rounded-lg
                          p-4
                          text-left

                          ${
                            answer
                            === option.id

                              ? "ring-2"

                              : ""
                          }
                        `}

                      >

                        <span
                          className="
                            font-semibold
                            mr-3
                          "
                        >
                          {
                            option.id
                              .toUpperCase()
                          }.
                        </span>

                        {option.text}

                      </button>

                    )
                  )
                }

              </div>

            )

            : (

              <textarea

                value={
                  answer
                }

                disabled={
                  result !== null
                }

                onChange={(event) =>
                  setAnswer(
                    event.target.value
                  )
                }

                placeholder="
                  Write your answer...
                "

                className="
                  w-full
                  min-h-32
                  border
                  rounded-lg
                  p-4
                "

              />

            )
          }


          {
            exercise.hint
            && !result
            && (

              <details>

                <summary
                  className="
                    cursor-pointer
                    font-medium
                  "
                >
                  Show hint
                </summary>


                <p
                  className="
                    mt-2
                    text-gray-500
                  "
                >
                  {exercise.hint}
                </p>

              </details>

            )
          }


          {!result && (

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
                py-3
                disabled:opacity-50
              "

            >

              {
                loading
                  ? "Checking..."
                  : "Check Answer"
              }

            </button>

          )}


          {result && (

            <div
              className="
                border-t
                pt-5
                space-y-4
              "
            >


              <h3
                className="
                  text-xl
                  font-semibold
                "
              >

                {
                  result.is_correct
                    ? "Correct"
                    : "Needs more practice"
                }

              </h3>


              <div>

                <div
                  className="
                    text-sm
                    font-medium
                  "
                >
                  Score
                </div>

                <div>
                  {
                    Math.round(
                      result.score
                      * 100
                    )
                  }%
                </div>

              </div>


              {!result.is_correct && (

                <div>

                  <div
                    className="
                      text-sm
                      font-medium
                    "
                  >
                    Correct answer
                  </div>

                  <div>
                    {
                      result.correct_answer
                    }
                  </div>

                </div>

              )}


              <div>

                <div
                  className="
                    text-sm
                    font-medium
                  "
                >
                  Explanation
                </div>

                <p
                  className="
                    mt-1
                    text-gray-600
                  "
                >
                  {result.explanation}
                </p>

              </div>


              <button

                onClick={
                  loadExercise
                }

                disabled={
                  loading
                }

                className="
                  border
                  rounded-lg
                  px-5
                  py-3
                  disabled:opacity-50
                "

              >

                {
                  loading
                    ? "Generating..."
                    : "Next Exercise"
                }

              </button>


            </div>

          )}


        </div>

      )}


    </div>

  );

}