import { BrowserRouter } from "react-router-dom";
import { Routes } from "react-router-dom";
import { Route } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import Dashboard from "../pages/Dashboard";
import Vocabulary from "../pages/Vocabulary";
import Flashcards from "../pages/Flashcards";
import Discover from "../pages/Discover";
import Settings from "../pages/Settings";
import GrammarQuiz from "../pages/GrammarQuiz";
import GrammarProgress from "../pages/GrammarProgress";
import Planner from "../pages/Planner";
import Login from "../pages/Login";
import Intelligence from "../pages/Intelligence";
import VocabularyIntelligence from "../pages/VocabularyIntelligence";

export default function AppRouter() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="*"
          element={
            <MainLayout>

              <Routes>

                <Route
                  path="/"
                  element={<Dashboard />}
                />

                <Route
                  path="/discover"
                  element={<Discover />}
                />

                <Route
                  path="/vocabulary"
                  element={<Vocabulary />}
                />

                <Route
                  path="/flashcards"
                  element={<Flashcards />}
                />

                <Route
                  path="/settings"
                  element={<Settings />}
                />

                <Route
                  path="/grammar-quiz"
                  element={<GrammarQuiz />}
                />

                <Route
                  path="/grammar-progress"
                  element={<GrammarProgress />}
                />

                <Route
                  path="/planner"
                  element={<Planner />}
                />

                <Route
                  path="/intelligence"
                  element={<Intelligence />}
                />

                <Route
                  path="/vocabulary-intelligence"
                  element={
                    <VocabularyIntelligence />
                  }
                />

              </Routes>

            </MainLayout>
          }
        />

      </Routes>

    </BrowserRouter>
  );
}