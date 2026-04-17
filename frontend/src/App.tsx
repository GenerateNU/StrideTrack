import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

const AthleteProfilePage = lazy(() => import("@/pages/AthleteProfilePage"));
const HistoryPage = lazy(() => import("@/pages/HistoryPage"));
const HomePage = lazy(() => import("@/pages/HomePage"));
const LoginPage = lazy(() => import("@/pages/LoginPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));
const RecordRunPage = lazy(() => import("@/pages/RecordRunPage"));
const RunAnalysisPage = lazy(() => import("@/pages/RunAnalysisPage"));
const VisualizationsPage = lazy(() => import("@/pages/VisualizationsPage"));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<QueryLoading />}>
        <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="*"
          element={
            <ProtectedRoute>
              <Routes>
                <Route element={<AppLayout />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/record" element={<RecordRunPage />} />
                  <Route path="/history" element={<HistoryPage />} />
                  <Route
                    path="/visualizations"
                    element={<VisualizationsPage />}
                  />
                  <Route
                    path="/athletes/:athleteId"
                    element={<AthleteProfilePage />}
                  />
                  <Route
                    path="/athletes/:athleteId/runs/:runId"
                    element={<RunAnalysisPage />}
                  />
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
