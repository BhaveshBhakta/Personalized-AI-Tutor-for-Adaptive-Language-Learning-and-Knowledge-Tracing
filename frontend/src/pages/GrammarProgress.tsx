import { useEffect } from "react";
import { useState } from "react";

import { api } from "../api/client";

export default function GrammarProgress() {

  const [progress, setProgress] =
    useState<any[]>([]);

  async function loadProgress() {

    const token =
      localStorage.getItem("token");

    const res =
      await api.get(
        "/grammar/progress",
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

    setProgress(res.data);
  }

  useEffect(() => {
    loadProgress();
  }, []);

  return (
    <div className="p-8">

      <h1
        className="
          text-3xl
          font-bold
          mb-8
        "
      >
        Grammar Progress
      </h1>

      {progress.map((item) => (

        <div
          key={item.id}
          className="
            border
            p-4
            rounded
            mb-3
          "
        >

          Topic ID:
          {" "}
          {item.topic_id}

          <br/>

          Mastery:
          {" "}
          {item.mastery_score}
          %

        </div>

      ))}

    </div>
  );
}