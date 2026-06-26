import { useState } from "react";
import { api } from "../api/client";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  async function handleLogin() {
    const res = await api.post(
      "/auth/login",
      {
        email,
        password,
      }
    );

    localStorage.setItem(
      "token",
      res.data.access_token
    );

    alert("Logged In");
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
        type="password"
        className="border p-2 w-full mt-3"
        placeholder="Password"
        onChange={(e) =>
          setPassword(e.target.value)
        }
      />

      <button
        className="mt-4 border px-4 py-2"
        onClick={handleLogin}
      >
        Login
      </button>
    </div>
  );
}