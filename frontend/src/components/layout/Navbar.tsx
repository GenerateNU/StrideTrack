import { useAuth } from "@/context/auth.context";

export function Navbar() {
  const { profile, logout } = useAuth();

  return (
    <nav className="bg-card border-b border-border px-6 py-3 flex justify-between items-center">
      <span className="font-medium text-foreground">{profile?.name}</span>
      <button
        onClick={logout}
        className="text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
      >
        Logout
      </button>
    </nav>
  );
}
