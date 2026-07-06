import {
  useState,
} from "react";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  api,
} from "../api/client";

import {
  useAuth,
} from "../context/AuthContext";


export default function Login() {

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const navigate =
    useNavigate();

  const location =
    useLocation();

  const {
    login,
  } = useAuth();


  async function handleLogin() {

    setError("");
    setLoading(true);

    try {

      const res =
        await api.post(
          "/auth/login",
          {
            email,
            password,
          }
        );


      login(
        res.data.access_token
      );


      const destination =
        location.state?.from || "/";


      navigate(
        destination,
        {
          replace: true,
        }
      );

    } catch {

      setError(
        "Invalid email or password"
      );

    } finally {

      setLoading(false);
    }
  }


  return (
    <div
      className="
        p-10
        max-w-md
        mx-auto
      "
    >

      <h1
        className="
          text-3xl
          font-bold
          mb-6
        "
      >
        Login
      </h1>


      <input
        type="email"
        value={email}
        className="
          border
          p-2
          w-full
        "
        placeholder="Email"
        onChange={(e) =>
          setEmail(
            e.target.value
          )
        }
      />


      <input
        type="password"
        value={password}
        className="
          border
          p-2
          w-full
          mt-3
        "
        placeholder="Password"
        onChange={(e) =>
          setPassword(
            e.target.value
          )
        }
        onKeyDown={(e) => {

          if (
            e.key === "Enter"
          ) {

            handleLogin();
          }
        }}
      />


      {error && (

        <div
          className="
            mt-3
            text-red-500
          "
        >
          {error}
        </div>

      )}


      <button
        className="
          mt-4
          border
          px-4
          py-2
          disabled:opacity-50
        "
        onClick={
          handleLogin
        }
        disabled={
          loading
        }
      >

        {
          loading
            ? "Logging in..."
            : "Login"
        }

      </button>

    </div>
  );
}