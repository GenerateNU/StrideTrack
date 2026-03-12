import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import LoginPage from "@/pages/LoginPage";
import HomePage from "@/pages/HomePage";
import RecordingPage from "@/pages/RecordRunPage";
import HistoryPage from "@/pages/HistoryPage";
import AthleteProfilePage from "@/pages/AthleteProfilePage";
import RunAnalysisPage from "@/pages/RunAnalysisPage";

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
                  <Route path="/history" element={<HistoryPage />} />
                  <Route
                    path="/athletes/:athleteId"
                    element={<AthleteProfilePage />}
                  />
                  <Route
                    path="/athletes/:athleteId/runs/:runId"
                    element={<RunAnalysisPage />}
                  />
                </Route>
                <Route path="/record" element={<RecordingPage />} />
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;