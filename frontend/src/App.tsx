import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ExamplePage } from "./pages/ExamplePage";
import LoginPage from "./pages/LoginPage";
import { supabase } from "./lib/supabaseClient";

function App() {
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      console.log("APP SESSION:", data.session);
      console.log("token:", data.session?.access_token);
      console.log("user id:", data.session?.user?.id);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log("APP AUTH EVENT:", event);
        console.log("APP SESSION FROM EVENT:", session);
        console.log("token:", session?.access_token);
        console.log("user id:", session?.user?.id);
      },
    );

    return () => listener.subscription.unsubscribe();
  }, []);

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
