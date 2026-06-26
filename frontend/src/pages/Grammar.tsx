import { useEffect } from "react";
import { useState } from "react";

import { api } from "../api/client";

export default function Grammar() {

  const [topics, setTopics] =
    useState<any[]>([]);

  async function loadTopics() {

    const res = await api.get(
      "/grammar/"
    );

    setTopics(res.data);
  }

  useEffect(() => {
    loadTopics();
  }, []);

  return (
    <div>

      <h1
        className="
          text-3xl
          font-bold
          mb-8
        "
      >
        Grammar
      </h1>

      <div
        className="
          grid
          gap-4
        "
      >

        {topics.map(
          (topic) => (

            <div
              key={topic.id}
              className="
                border
                rounded-lg
                p-4
              "
            >

              <div
                className="
                  text-xl
                  font-bold
                "
              >
                {topic.title}
              </div>

              <div
                className="
                  mt-2
                "
              >
                {topic.explanation}
              </div>

            </div>

          )
        )}

      </div>

    </div>
  );
}