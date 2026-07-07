import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Dashboard() {

  const [data, setData] =
    useState<any>(null);

  const [plan, setPlan] =
    useState<any>(null);

  async function loadDashboard() {

    const dashboard =
      await api.get(
        "/dashboard/"
      );

    const study =
      await api.get(
        "/dashboard/study-plan"
      );

    setData(
      dashboard.data
    );

    setPlan(
      study.data
    );
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  if (!data || !plan)
    return <div>Loading...</div>;

  return (

    <div className="space-y-8">

      <h1
        className="
          text-4xl
          font-bold
        "
      >
        Dashboard
      </h1>

      <div
        className="
          grid
          md:grid-cols-3
          gap-5
        "
      >

        <Stat
          title="Words"
          value={data.total_words}
        />

        <Stat
          title="XP"
          value={data.xp}
        />

        <Stat
          title="Streak"
          value={data.streak}
        />

        <Stat
          title="Due Reviews"
          value={data.due_reviews}
        />

        <Stat
          title="Average Mastery"
          value={
            `${data.average_mastery}%`
          }
        />

        <Stat
          title="Retention"
          value={
            `${data.average_retention}%`
          }
        />

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
          "
        >
          Today's Study Plan
        </h2>

        <div className="mt-4">

          <div>
            Reviews:
            {" "}
            {plan.reviews}
          </div>

          <div>
            New Words:
            {" "}
            {plan.new_words}
          </div>

          <div>
            Grammar:
            {" "}
            {plan.grammar_exercises}
          </div>

          <div>
            Conversation:
            {" "}
            {plan.conversation_minutes}
            {" "}
            min
          </div>

        </div>

      </div>

    </div>

  );

}

function Stat({

  title,

  value,

}: {

  title: string;

  value: any;

}) {

  return (

    <div
      className="
        border
        rounded-xl
        p-5
      "
    >

      <div
        className="
          text-gray-500
        "
      >
        {title}
      </div>

      <div
        className="
          text-3xl
          font-bold
          mt-2
        "
      >
        {value}
      </div>

    </div>

  );

}