import { BrowserRouter, Routes, Route} from 'react-router-dom';
import { ExamplePage } from './pages/ExamplePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ExamplePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
