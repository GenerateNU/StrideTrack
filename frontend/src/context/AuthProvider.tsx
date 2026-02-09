import { useEffect, useMemo, useState, type ReactNode } from "react";
import { supabase } from "../lib/supabase";
import { AuthContext, type AuthMode } from "./authContext";
import type { Session } from "@supabase/supabase-js";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AuthMode>("none");
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const devToken = localStorage.getItem("dev-token");
    if (devToken) {
      setMode("dev");
      setSession(null);
      setLoading(false);
      return;
    }

    const sync = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session ?? null);
      setMode(data.session ? "google" : "none");
      setLoading(false);
    };

    sync();

    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => {
      // If dev-token is present, ignore Supabase changes
      if (localStorage.getItem("dev-token")) return;

      setSession(newSession);
      setMode(newSession ? "google" : "none");
      setLoading(false);
    });

    return () => data.subscription.unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    // keep your existing redirect behavior
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: window.location.origin },
    });
  };

  const loginAsDev = () => {
    localStorage.setItem("dev-token", "dev-token");
    setSession(null);
    setMode("dev");
  };

  const logout = async () => {
    localStorage.removeItem("dev-token");
    await supabase.auth.signOut();
    setSession(null);
    setMode("none");
  };

  const value = useMemo(
    () => ({
      mode,
      session,
      loading,
      loginWithGoogle,
      loginAsDev,
      logout,
    }),
    [mode, session, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// import { useEffect, useState, type ReactNode } from "react";
// import type { Session } from "@supabase/supabase-js";
// import { supabase } from "../lib/supabase";
// import { AuthContext } from "./authContext";

// export function AuthProvider({ children }: { children: ReactNode }) {
//   const [session, setSession] = useState<Session | null>(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     supabase.auth.getSession().then(({ data: { session } }) => {
//       setSession(session);
//       setLoading(false);
//     });

//     const {
//       data: { subscription },
//     } = supabase.auth.onAuthStateChange((_event, session) =>
//       setSession(session)
//     );

//     return () => subscription.unsubscribe();
//   }, []);

//   const signInWithGoogle = async () => {
//     await supabase.auth.signInWithOAuth({
//       provider: "google",
//       options: { redirectTo: window.location.origin },
//     });
//   };

//   const signOut = async () => {
//     await supabase.auth.signOut();
//   };

//   return (
//     <AuthContext.Provider
//       value={{ session, loading, signInWithGoogle, signOut }}
//     >
//       {children}
//     </AuthContext.Provider>
//   );
// }
