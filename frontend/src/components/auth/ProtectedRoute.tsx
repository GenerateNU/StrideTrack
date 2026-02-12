import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/auth.context";
import { QueryLoading } from "../QueryLoading";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { mode, loading } = useAuth();

  if (loading) {
    return <QueryLoading />;
  }

  if (mode === "none") {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
