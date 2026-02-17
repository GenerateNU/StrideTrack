import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import VisualizationsPage from "@/pages/VisualizationsPage";

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
                <Route path="/" element={<VisualizationsPage />} />
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
