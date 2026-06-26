import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

api.interceptors.request.use(
  (config) => {

    const token =
      localStorage.getItem(
        "token"
      );

    console.log(
      "TOKEN BEING SENT:",
      token
    );

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;

    }

    return config;
  }
);