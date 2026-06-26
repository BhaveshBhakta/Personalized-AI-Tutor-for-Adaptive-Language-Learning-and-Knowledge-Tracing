import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Intelligence() {

  const [data, setData] =
    useState<any>(null);

  async function loadData() {

    const res =
      await api.get(
        "/intelligence/weak-topic"
      );

    setData(res.data);
  }

  useEffect(() => {
    loadData();
  }, []);

  if (!data) {
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
          text-3xl
          font-bold
          mb-6
        "
      >
        Learner Intelligence
      </h1>

      <pre>
        {JSON.stringify(
          data,
          null,
          2
        )}
      </pre>

    </div>
  );
}