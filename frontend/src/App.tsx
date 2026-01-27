import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ExamplePage } from "./pages/ExamplePage";
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ExamplePage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
