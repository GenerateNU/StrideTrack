/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { Capacitor } from "@capacitor/core";
import { supabase } from "@/lib/supabase";
import { getDevToken, setDevToken, clearDevToken } from "@/lib/dev";
import api from "@/lib/api";
import type { Profile, Coach } from "@/types/auth.types";

export type { Profile, Coach };

export type AuthMode = "none" | "dev" | "google";

export interface AuthContextValue {
  mode: AuthMode;
  profile: Profile | null;
  coach: Coach | null;
  loading: boolean;
  error: Error | null;
  loginWithGoogle: () => Promise<void>;
  loginAsDev: () => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AuthMode>("none");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [coach, setCoach] = useState<Coach | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      const { data } = await api.get<Profile>("/auth/me");
      setProfile(data);
      setError(null);

      // If user is a coach, fetch coach data
      if (data.role === "coach") {
        try {
          const { data: coachData } = await api.get<Coach>("/auth/me/coach");
          setCoach(coachData);
        } catch (err) {
          console.error("Failed to fetch coach:", err);
          setCoach(null);
        }
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      setError(err as Error);
      setProfile(null);
      setCoach(null);
    }
  }, []);

  const checkAuth = useCallback(async () => {
    setLoading(true);

    const devToken = getDevToken();
    if (devToken) {
      setMode("dev");
      await fetchProfile();
      setLoading(false);
      return;
    }

    try {
      const { data } = await supabase.auth.getSession();
      if (data.session?.access_token) {
        setMode("google");
        await fetchProfile();
      } else {
        setMode("none");
        setProfile(null);
        setCoach(null);
      }
    } catch (err) {
      console.error("Auth check failed:", err);
      setMode("none");
      setProfile(null);
      setCoach(null);
    } finally {
      setLoading(false);
    }
  }, [fetchProfile]);

  useEffect(() => {
    checkAuth();

    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      if (getDevToken()) return;

      if (event === "SIGNED_IN" && session?.access_token) {
        setMode("google");
        fetchProfile();
      } else if (event === "SIGNED_OUT") {
        setMode("none");
        setProfile(null);
        setCoach(null);
      }
      setLoading(false);
    });

    // Listen for deep-link redirects from OAuth on native platforms
    let appUrlListener: { remove: () => Promise<void> } | undefined;
    if (Capacitor.isNativePlatform()) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (import(/* @vite-ignore */ "@capacitor/app") as Promise<any>).then(
        (mod) => {
          mod.App.addListener(
            "appUrlOpen",
            ({ url }: { url: string }) => {
              // URL looks like: com.stridetrack.app://auth/callback#access_token=...&refresh_token=...
              const hashIndex = url.indexOf("#");
              if (hashIndex === -1) return;

              const params = new URLSearchParams(url.substring(hashIndex + 1));
              const accessToken = params.get("access_token");
              const refreshToken = params.get("refresh_token");

              if (accessToken && refreshToken) {
                supabase.auth.setSession({
                  access_token: accessToken,
                  refresh_token: refreshToken,
                });
              }
            }
          ).then((listener: { remove: () => Promise<void> }) => {
            appUrlListener = listener;
          });
        }
      );
    }

    return () => {
      data.subscription.unsubscribe();
      appUrlListener?.remove();
    };
  }, [checkAuth, fetchProfile]);

  const loginWithGoogle = async () => {
    clearDevToken();
    const redirectTo = Capacitor.isNativePlatform()
      ? "com.stridetrack.app://auth/callback"
      : window.location.origin;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo },
    });
    if (error) throw error;
  };

  const loginAsDev = useCallback(async () => {
    setDevToken();
    setMode("dev");
    await fetchProfile();
  }, [fetchProfile]);

  const logout = async () => {
    clearDevToken();
    await supabase.auth.signOut();
    setProfile(null);
    setCoach(null);
    setMode("none");
    setError(null);
  };

  const refreshProfile = useCallback(async () => {
    setError(null);
    await fetchProfile();
  }, [fetchProfile]);

  const value = useMemo(
    () => ({
      mode,
      profile,
      coach,
      loading,
      error,
      loginWithGoogle,
      loginAsDev,
      logout,
      refreshProfile,
    }),
    [mode, profile, coach, loading, error, loginAsDev, refreshProfile]
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
