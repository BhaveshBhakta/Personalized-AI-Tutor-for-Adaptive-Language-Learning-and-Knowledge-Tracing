import { useState } from "react";
import { api } from "../api/client";

export default function Register() {
  const [email, setEmail] =
    useState("");

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  async function handleRegister() {
    await api.post(
      "/auth/register",
      {
        email,
        username,
        password,
      }
    );

    alert("Registered");
  }

  return (
    <div className="p-10 max-w-md mx-auto">
      <input
        className="border p-2 w-full"
        placeholder="Email"
        onChange={(e) =>
          setEmail(e.target.value)
        }
      />

      <input
        className="border p-2 w-full mt-3"
        placeholder="Username"
        onChange={(e) =>
          setUsername(e.target.value)
        }
      />

      <input
        type="password"
        className="border p-2 w-full mt-3"
        placeholder="Password"
        onChange={(e) =>
          setPassword(e.target.value)
        }
      />

      <button
        className="mt-4 border px-4 py-2"
        onClick={handleRegister}
      >
        Register
      </button>
    </div>
  );
}