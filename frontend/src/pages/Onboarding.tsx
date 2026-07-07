import { useState } from "react";
import { api } from "../api/client";

export default function Onboarding() {
  const [level, setLevel] =
    useState("A1");

  const [goal, setGoal] =
    useState(30);

  async function submit() {

    await api.post(
      "/profile",
      {
        target_level: level,
        daily_goal_minutes: goal,
      }
    );

    alert("Profile Saved");
  }

  return (
    <div className="max-w-lg mx-auto p-10">

      <h1 className="text-3xl font-bold mb-8">
        German Learning Setup
      </h1>

      <select
        className="border p-3 w-full"
        value={level}
        onChange={(e) =>
          setLevel(
            e.target.value
          )
        }
      >
        <option>A1</option>
        <option>A2</option>
        <option>B1</option>
        <option>B2</option>
      </select>

      <select
        className="border p-3 w-full mt-4"
        value={goal}
        onChange={(e) =>
          setGoal(
            Number(
              e.target.value
            )
          )
        }
      >
        <option value={15}>
          15 min/day
        </option>

        <option value={30}>
          30 min/day
        </option>

        <option value={60}>
          60 min/day
        </option>
      </select>

      <button
        onClick={submit}
        className="
          mt-6
          px-4
          py-2
          border
        "
      >
        Save
      </button>

    </div>
  );
}