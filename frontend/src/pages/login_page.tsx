import { supabase } from "../lib/supabase";

const ENV = import.meta.env.VITE_ENVIRONMENT;

export default function LoginPage() {
  const handleGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: window.location.origin },
    });
  };

  const handleDevLogin = () => {
    localStorage.setItem("dev-token", "dev-token");
    window.location.href = "/"; // or wherever your main page is
  };

  const handleDevLogout = () => {
    localStorage.removeItem("dev-token");
    window.location.reload();
  };

  return (
    <div style={{ display: "flex", gap: 12 }}>
      <button onClick={handleGoogle}>Sign in with Google</button>

      {ENV === "development" && (
        <>
          <button onClick={handleDevLogin}>Login as Dev</button>
          <button onClick={handleDevLogout}>Clear Dev Login</button>
        </>
      )}
    </div>
  );
}



// import { useEffect } from "react";
// import { supabase } from "../lib/supabase";

// export default function LoginPage() {
//   useEffect(() => {
//     const checkSession = async () => {
//       const { data } = await supabase.auth.getSession();
//       console.log("SESSION:", data.session);
//     };

//     checkSession();
//   }, []);

//   const handleGoogle = async () => {
//     await supabase.auth.signInWithOAuth({
//       provider: "google",
//       options: { redirectTo: window.location.origin },
//     });
//   };

//   return <button onClick={handleGoogle}>Sign in with Google</button>;
// }
