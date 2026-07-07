import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  api,
} from "../api/client";


interface User {
  id: number;
  email: string;
  username: string;
}


interface AuthContextType {

  user: User | null;

  isAuthenticated: boolean;

  loading: boolean;

  login: (
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => void;

}


const AuthContext =
  createContext<
    AuthContextType | undefined
  >(undefined);


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {

  const [
    user,
    setUser,
  ] = useState<User | null>(
    null
  );


  const [
    loading,
    setLoading,
  ] = useState(true);


  useEffect(() => {

    async function restoreSession() {

      const token =
        localStorage.getItem(
          "token"
        );


      if (!token) {

        setLoading(false);

        return;

      }


      try {

        const response =
          await api.get(
            "/auth/me"
          );


        setUser(
          response.data
        );


      } catch {

        localStorage.removeItem(
          "token"
        );

        setUser(null);

      } finally {

        setLoading(false);

      }

    }


    restoreSession();

  }, []);

  useEffect(() => {

    function handleUnauthorized() {

      localStorage.removeItem(
        "token"
      );

      setUser(null);

    }


    window.addEventListener(
      "auth:unauthorized",
      handleUnauthorized
    );


    return () => {

      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized
      );

    };

  }, []);


  async function login(
    email: string,
    password: string
  ) {

    const response =
      await api.post(
        "/auth/login",
        {
          email,
          password,
        }
      );


    const token =
      response.data.access_token;


    localStorage.setItem(
      "token",
      token
    );


    try {

      const userResponse =
        await api.get(
          "/auth/me"
        );


      setUser(
        userResponse.data
      );


    } catch (error) {

      localStorage.removeItem(
        "token"
      );

      setUser(null);

      throw error;

    }

  }


  function logout() {

    localStorage.removeItem(
      "token"
    );

    setUser(null);

  }


  const value: AuthContextType = {

    user,

    isAuthenticated:
      user !== null,

    loading,

    login,

    logout,

  };


  return (

    <AuthContext.Provider
      value={value}
    >

      {children}

    </AuthContext.Provider>

  );

}


export function useAuth() {

  const context =
    useContext(
      AuthContext
    );


  if (!context) {

    throw new Error(
      "useAuth must be used inside AuthProvider"
    );

  }


  return context;

}