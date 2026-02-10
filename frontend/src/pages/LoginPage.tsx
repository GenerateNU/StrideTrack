import { QueryLoading } from "@/components/QueryLoading";
import { useAuth } from "@/context/AuthenticationContext";

const ENV = import.meta.env.VITE_ENVIRONMENT;

export default function LoginPage() {
  const { user, loading, loginAsDev, loginWithGoogle, logout } = useAuth();
  const devToken = localStorage.getItem("dev-token");

  return loading ? (
    <QueryLoading /> //loading
  ) : !devToken && !user ? ( //if we are logged out
    <>
      <div>Currently logged out</div>
      <button onClick={loginWithGoogle}>Sign in with Google</button>
      <button onClick={loginAsDev}>Login as Dev</button>{" "}
    </>
  ) : ENV === "development" && devToken && !user ? ( //already in dev
    <>
      <div>Logged in as Dev</div>
      <button onClick={logout}>Clear Dev Login</button>
    </>
  ) : (
    <>
      <div>Logged in as Google {user?.email}</div>
      <button onClick={logout}>Sign out of Google</button>
    </>
  );
}
