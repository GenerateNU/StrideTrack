import { createContext } from "react";
import type { Session } from "@supabase/supabase-js";

export type AuthMode = "none" | "dev" | "google";

export type AuthContextValue = {
  mode: AuthMode;
  session: Session | null;
  loading: boolean;
  loginWithGoogle: () => Promise<void>;
  loginAsDev: () => void;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

// import React, {
//   createContext,
//   useContext,
//   useEffect,
//   useMemo,
//   useState,
// } from "react";
// import { supabase } from "../lib/supabase";

// type AuthMode = "none" | "dev" | "google";

// type AuthContextValue = {
//   mode: "none" | "dev" | "google";
//   logout: () => Promise<void>;
// };

// const AuthContext = createContext<AuthContextValue | null>(null);

// export function AuthProvider({ children }: { children: React.ReactNode }) {
//   const [mode, setMode] = useState<AuthMode>("none");

//   useEffect(() => {
//     const devToken = localStorage.getItem("dev-token");
//     if (devToken) {
//       setMode("dev");
//       return;
//     }

//     const sync = async () => {
//       const { data } = await supabase.auth.getSession();
//       setMode(data.session ? "google" : "none");
//     };

//     sync();

//     const { data: sub } = supabase.auth.onAuthStateChange(() => {
//       sync();
//     });

//     return () => {
//       sub.subscription.unsubscribe();
//     };
//   }, []);

//   const logout = async () => {
//     localStorage.removeItem("dev-token");
//     await supabase.auth.signOut();
//     setMode("none");
//   };

//   const value = useMemo(() => ({ mode, logout }), [mode]);

//   return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
// }

// export function useAuthContext() {
//   const ctx = useContext(AuthContext);
//   if (!ctx) throw new Error("useAuthContext must be used within AuthProvider");
//   return ctx;
// }

// // import { createContext } from 'react'
// // import type { Session } from '@supabase/supabase-js'

// // export interface AuthContextType {
// //   session: Session | null
// //   loading: boolean
// //   signInWithGoogle: () => Promise<void>
// //   signOut: () => Promise<void>
// // }

// // export const AuthContext = createContext<AuthContextType | undefined>(undefined)
