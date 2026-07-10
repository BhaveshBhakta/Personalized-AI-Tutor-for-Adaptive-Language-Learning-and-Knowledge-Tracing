import type {
  ReactNode,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  BarChart3,
  BookOpen,
  Brain,
  CalendarDays,
  FileText,
  Languages,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Search,
  Settings,
  Dumbbell,
} from "lucide-react";

import {
  useAuth,
} from "../context/AuthContext";


export default function MainLayout({
  children,
}: {
  children: ReactNode;
}) {

  const {
    logout,
  } = useAuth();


  function handleLogout() {

    logout();

  }

  return (

    <div className="flex min-h-screen">

      <aside
        className="
          w-64
          border-r
          p-6
          flex
          flex-col
        "
      >

        <div
          className="
            text-2xl
            font-bold
            mb-8
          "
        >
          German OS
        </div>


        <nav
          className="
            flex
            flex-col
            gap-5
          "
        >

          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/"
          >
            <LayoutDashboard size={18} />

            Dashboard
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/planner"
          >
            <CalendarDays size={18} />

            Planner
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/intelligence"
          >
            <Brain size={18} />

            Intelligence
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/discover"
          >
            <Search size={18} />

            Discover
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/vocabulary"
          >
            <BookOpen size={18} />

            Vocabulary
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/flashcards"
          >
            <Brain size={18} />

            Flashcards
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/grammar"
          >
            <Languages size={18} />

            Grammar
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/grammar-progress"
          >
            <BarChart3 size={18} />

            Grammar Progress
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/documents"
          >
            <FileText size={18} />

            Documents
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/ai-chat"
          >
            <MessageSquare size={18} />

            AI Tutor
          </Link>


          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/settings"
          >
            <Settings size={18} />

            Settings
          </Link>

          <Link
            className="
              flex
              items-center
              gap-3
            "
            to="/adaptive-practice"
          >
            <Dumbbell size={18} />
            Adaptive Practice
          </Link>
        </nav>


        <button
          type="button"
          onClick={
            handleLogout
          }
          className="
            mt-auto
            flex
            items-center
            gap-3
            border
            rounded-lg
            px-4
            py-3
            text-left
          "
        >

          <LogOut size={18} />

          Logout

        </button>

      </aside>


      <main
        className="
          flex-1
          p-8
        "
      >

        {children}

      </main>

    </div>

  );
}