import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/auth.context";
import { config } from "@/lib/config";
import { QueryLoading } from "@/components/QueryLoading";

export default function LoginPage() {
  const { mode, loading, loginAsDev, loginWithGoogle } = useAuth();

  if (loading) {
    return <QueryLoading />;
  }

  if (mode !== "none") {
    return <Navigate to="/" replace />;
  }

  return (
    <div>
      <button onClick={loginWithGoogle}>Sign in with Google</button>
      <div />
      {config.development.bypassAuth && (
        <button onClick={loginAsDev}>Login as Dev</button>
      )}
    </div>
  );
}
