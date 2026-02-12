import { useEffect, useState } from "react";
import api from "../lib/api";
import { useAuth } from "./useAuth";

interface User {
  user_id: string;
  email: string;
}

export function useCurrentUser() {
  const { session } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) {
      setUser(null);
      return;
    }

    const fetchUser = async () => {
      setLoading(true);
      try {
        const { data } = await api.get("/api/auth/me");
        setUser(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch user");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [session]);

  return { user, loading, error };
}
