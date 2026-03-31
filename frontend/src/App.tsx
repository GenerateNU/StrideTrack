import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import AthleteProfilePage from "@/pages/AthleteProfilePage";
import HistoryPage from "@/pages/HistoryPage";
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RecordingPage from "@/pages/RecordRunPage";
import RunAnalysisPage from "@/pages/RunAnalysisPage";
import VisualizationsPage from "@/pages/VisualizationsPage";
import { BrowserRouter, Route, Routes } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="*"
          element={
            <ProtectedRoute>
              <Routes>
                <Route element={<AppLayout />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/record" element={<RecordingPage />} />
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
                </Route>
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
