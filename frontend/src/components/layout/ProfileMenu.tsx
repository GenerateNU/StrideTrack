import { Moon, Sun, LogOut } from "lucide-react";

interface ProfileMenuProps {
  profile: { name?: string; email?: string } | null;
  theme: string;
  toggleTheme: () => void;
  onLogout: () => void;
  className?: string;
}

export function ProfileMenu({
  profile,
  theme,
  toggleTheme,
  onLogout,
  className = "absolute right-0 top-full mt-2 w-60",
}: ProfileMenuProps) {
  return (
    <div
      className={`${className} rounded-2xl border border-border bg-card p-2 shadow-xl shadow-foreground/5`}
    >
      <div className="px-3 py-3">
        <p className="text-sm font-semibold text-foreground">
          {profile?.name ?? "Coach"}
        </p>
        <p className="text-xs text-muted-foreground">{profile?.email}</p>
      </div>

      <div className="mx-2 h-px bg-border" />

      <button
        onClick={toggleTheme}
        className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-foreground transition-colors hover:bg-secondary"
      >
        {theme === "light" ? (
          <Moon className="h-4 w-4" />
        ) : (
          <Sun className="h-4 w-4" />
        )}
        {theme === "light" ? "Dark Mode" : "Light Mode"}
      </button>

      <div className="mx-2 h-px bg-border" />

      <button
        onClick={onLogout}
        className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-destructive transition-colors hover:bg-secondary"
      >
        <LogOut className="h-4 w-4" />
        Log Out
      </button>
    </div>
  );
}
