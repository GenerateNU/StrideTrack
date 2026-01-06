import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { ExamplePage } from './pages/ExamplePage';

function HomePage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-4">StrideTrack</h1>
      <p className="text-slate-400 mb-6">
        Biomechanical data collection and analysis for track and field coaches.
      </p>
      <Link
        to="/example"
        className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        View Training Runs Example
      </Link>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/example" element={<ExamplePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
