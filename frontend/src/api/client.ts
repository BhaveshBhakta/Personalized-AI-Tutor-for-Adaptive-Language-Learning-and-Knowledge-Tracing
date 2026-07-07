import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";


interface RetryConfig
  extends InternalAxiosRequestConfig {

  _retry?: boolean;

}


export const api = axios.create({

  baseURL:
    "http://localhost:8000",

  withCredentials: true,

});


api.interceptors.request.use(

  (config) => {

    const token =
      localStorage.getItem(
        "token"
      );


    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;

    }


    return config;

  }

);


api.interceptors.response.use(

  (response) =>
    response,


  async (
    error: AxiosError
  ) => {

    const originalRequest =
      error.config as
        RetryConfig | undefined;


    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes(
        "/auth/login"
      ) &&
      !originalRequest.url?.includes(
        "/auth/refresh"
      )
    ) {

      originalRequest._retry =
        true;


      try {

        const refreshResponse =
          await api.post(
            "/auth/refresh"
          );


        const newToken =
          refreshResponse.data
            .access_token;


        localStorage.setItem(
          "token",
          newToken
        );


        originalRequest.headers.Authorization =
          `Bearer ${newToken}`;


        return api(
          originalRequest
        );


      } catch {

        localStorage.removeItem(
          "token"
        );


        window.dispatchEvent(
          new Event(
            "auth:unauthorized"
          )
        );


        return Promise.reject(
          error
        );

      }

    }


    return Promise.reject(
      error
    );

  }

);