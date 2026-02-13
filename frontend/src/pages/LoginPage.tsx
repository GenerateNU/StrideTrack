import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/auth.context";
import { config } from "@/lib/config";
import { QueryLoading } from "@/components/QueryLoading";
import GoogleSignInButton from "@/components/auth/GoogleSignInButton";
import logo from "@/assets/stridetrack-logo.png";

export default function LoginPage() {
  const { mode, loading, loginAsDev, loginWithGoogle } = useAuth();

  if (loading) {
    return <QueryLoading />;
  }

  if (mode !== "none") {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center bg-[#0a0a0a] px-6">
      {/* Logo + Branding */}
      <div className="mb-12 flex flex-col items-center gap-3">
        <img
          src={logo}
          alt="StrideTrack"
          className="h-20 w-auto"
        />
        <p className="text-sm tracking-wide text-neutral-500">
          Track every stride. Coach every athlete.
        </p>
      </div>

      {/* Sign In */}
      <div className="flex w-full max-w-[300px] flex-col items-center gap-4">
        <GoogleSignInButton onClick={loginWithGoogle} />
      </div>

      {/* Dev Login — temporary, minimal */}
      {config.development.bypassAuth && (
        <button
          onClick={loginAsDev}
          className="mt-8 text-xs text-neutral-600 underline decoration-neutral-700 underline-offset-2 transition-colors hover:text-neutral-400"
        >
          Continue as dev user
        </button>
      )}
    </div>
  );
}