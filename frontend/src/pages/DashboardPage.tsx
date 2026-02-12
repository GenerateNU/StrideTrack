import { useAuth } from "@/context/auth.context";

export default function DashboardPage() {
  const { profile, mode, logout } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Name: {profile?.name}</p>
      <p>Email: {profile?.email}</p>
      <p>Auth Method: {mode === "google" ? "Google" : "Dev"}</p>
      <button onClick={logout}>Sign out</button>
    </div>
  );
}
