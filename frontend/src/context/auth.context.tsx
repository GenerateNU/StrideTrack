/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { User } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export type AuthMode = "none" | "dev" | "google";

export type AuthContextValue = {
  mode: AuthMode;
  user: User | null;
  loading: boolean;
  loginWithGoogle: () => Promise<void>;
  loginAsDev: () => void;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AuthMode>("none");
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    //if previously clicked Login as Dev, we stored:
    // localStorage["dev-token"] = "dev-token"
    //so when app loads, we immediately  enter dev mode
    const devToken = localStorage.getItem("dev-token");
    if (devToken) {
      setMode("dev");
      setUser(null);
      setLoading(false);
      return;
    }

    const sync = async () => {
      const { data } = await supabase.auth.getUser();
      setUser(data.user ?? null);
      setMode(data.user ? "google" : "none");
      setLoading(false);
    };

    sync();

    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => {
      // If dev-token is present, ignore Supabase changes
      if (localStorage.getItem("dev-token")) return;

      setUser(newSession?.user ?? null);
      setMode(newSession ? "google" : "none");
      setLoading(false);
    });

    return () => data.subscription.unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    // keep your existing redirect behavior
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: window.location.origin },
    });
    if (error) throw error;
  };

  const loginAsDev = () => {
    localStorage.setItem("dev-token", "dev-token");
    setUser(null);
    console.error("Logged in as Dev");
    setMode("dev");
    setLoading(false);
  };

  const logout = async () => {
    localStorage.removeItem("dev-token");
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    setUser(null);
    setMode("none");
  };

  const value = useMemo(
    () => ({
      mode,
      user,
      loading,
      loginWithGoogle,
      loginAsDev,
      logout,
    }),
    [mode, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
