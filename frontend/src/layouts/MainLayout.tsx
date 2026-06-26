import { Link } from "react-router-dom";
import { LayoutDashboard } from "lucide-react";
import { Search } from "lucide-react";
import { BookOpen } from "lucide-react";
import { Brain } from "lucide-react";
import { Settings } from "lucide-react";
import { CalendarDays } from "lucide-react";
import { Languages } from "lucide-react";
import { BarChart3 } from "lucide-react";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">

      <aside
        className="
          w-64
          border-r
          p-6
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
            to="/settings"
          >
            <Settings size={18} />
            Settings
          </Link>

        </nav>

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