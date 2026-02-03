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
