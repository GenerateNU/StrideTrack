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
    <div className="relative flex min-h-dvh flex-col items-center justify-center overflow-hidden bg-neutral-100 px-5">
      {/* Warm radial glow */}
      <div
        className="pointer-events-none absolute -top-1/4 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full opacity-15 blur-[120px]"
        style={{
          background:
            "radial-gradient(circle, #fb8b24 0%, #f77f00 40%, transparent 70%)",
        }}
      />

      {/* Subtle secondary glow at bottom */}
      <div
        className="pointer-events-none absolute -bottom-1/4 left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full opacity-10 blur-[100px]"
        style={{
          background: "radial-gradient(circle, #fb8b24 0%, transparent 70%)",
        }}
      />

      {/* Noise texture overlay */}
      <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.03]">
        <filter id="noise">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.8"
            numOctaves="4"
            stitchTiles="stitch"
          />
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" />
      </svg>

      {/* Content */}
      <div className="relative z-10 flex w-full max-w-sm flex-col items-center">
        {/* Logo + Tagline */}
        <div className="mb-8 flex flex-col items-center gap-3">
          <img src={logo} alt="StrideTrack" className="h-35 w-auto" />
          <p className="text-sm tracking-wide text-neutral-500">
            Track every stride.
          </p>
        </div>

        {/* Card */}
        <div className="w-full rounded-2xl bg-white p-8 shadow-xl shadow-black/10 border border-neutral-200">
          <h1 className="text-center text-xl font-bold text-neutral-900">
            Welcome back
          </h1>
          <p className="mt-1 text-center text-sm text-neutral-500">
            Sign in to continue to StrideTrack
          </p>

          {/* Google Button */}
          <div className="mt-6">
            <GoogleSignInButton onClick={loginWithGoogle} />
          </div>

          {/* Dev Login */}
          {config.development.bypassAuth && (
            <>
              <div className="my-5 flex items-center gap-3">
                <div className="h-px flex-1 bg-neutral-200" />
                <span className="text-xs font-medium tracking-wider text-neutral-400">
                  OR
                </span>
                <div className="h-px flex-1 bg-neutral-200" />
              </div>

              <button
                onClick={loginAsDev}
                className="w-full cursor-pointer rounded-lg bg-neutral-100 py-3.5 text-[15px] font-medium text-neutral-700 transition-colors hover:bg-neutral-200"
              >
                Continue as Dev
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
