const API_URL =
  "http://localhost:8000";


async function refreshAccessToken():
  Promise<string | null> {

  try {

    const response =
      await fetch(
        `${API_URL}/auth/refresh`,
        {
          method: "POST",

          credentials: "include",
        }
      );


    if (!response.ok) {

      return null;

    }


    const data =
      await response.json();


    const token =
      data.access_token;


    localStorage.setItem(
      "token",
      token
    );


    return token;

  } catch {

    return null;

  }

}


interface StreamRequestOptions {

  method?: string;

  body?: unknown;

  headers?: Record<
    string,
    string
  >;

}


export async function authenticatedFetch(
  path: string,
  options: StreamRequestOptions = {}
): Promise<Response> {

  let token =
    localStorage.getItem(
      "token"
    );


  const makeRequest = (
    accessToken: string | null
  ) => {

    return fetch(
      `${API_URL}${path}`,
      {
        method:
          options.method || "GET",

        credentials:
          "include",

        headers: {

          "Content-Type":
            "application/json",

          ...options.headers,

          ...(accessToken
            ? {
                Authorization:
                  `Bearer ${accessToken}`,
              }
            : {}),
        },

        body:
          options.body !== undefined
            ? JSON.stringify(
                options.body
              )
            : undefined,
      }
    );

  };


  let response =
    await makeRequest(
      token
    );


  if (
    response.status === 401
  ) {

    token =
      await refreshAccessToken();


    if (!token) {

      localStorage.removeItem(
        "token"
      );


      window.dispatchEvent(
        new Event(
          "auth:unauthorized"
        )
      );


      return response;

    }


    response =
      await makeRequest(
        token
      );

  }


  return response;
}