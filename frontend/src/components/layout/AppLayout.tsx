import { useState, useRef, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";
import { Sidebar } from "./Sidebar";
import { UserCircle, LogOut, Plus, Moon, Sun } from "lucide-react";
import { useAuth } from "@/context/auth.context";
import { AddAthleteModal } from "@/components/athletes/AddAthleteModal";
import { useTheme } from "@/hooks/useTheme";
import logo from "@/assets/stridetrack-logo.png";

export function AppLayout() {
  const { logout, profile } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const [addAthleteOpen, setAddAthleteOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <div
        className="pointer-events-none absolute left-1/2 top-0 h-[300px] w-[500px] -translate-x-1/2 rounded-full opacity-[0.06] blur-[100px] md:left-[calc(50%+7rem)]"
        style={{
          background:
            "radial-gradient(circle, hsl(var(--primary)) 0%, transparent 70%)",
        }}
      />

      {/* Desktop sidebar */}
      <Sidebar />

      {/* Mobile header — hidden on desktop since sidebar has logo */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card/95 px-5 py-4 backdrop-blur-sm md:hidden">
        <img src={logo} alt="StrideTrack" className="h-9 w-auto" />
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-muted-foreground transition-colors"
          >
            <UserCircle className="h-5 w-5" />
          </button>

          {menuOpen && (
            <ProfileMenu
              profile={profile}
              theme={theme}
              toggleTheme={toggleTheme}
              onAddAthlete={() => {
                setMenuOpen(false);
                setAddAthleteOpen(true);
              }}
              onLogout={() => {
                setMenuOpen(false);
                logout();
              }}
            />
          )}
        </div>
      </header>

      {/* Desktop top bar — only profile menu, no logo (sidebar has it) */}
      <div className="sticky top-0 z-40 hidden border-b border-border bg-card/95 backdrop-blur-sm md:block md:pl-56">
        <div className="flex items-center justify-end px-6 py-3">
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-muted-foreground transition-colors"
            >
              <UserCircle className="h-5 w-5" />
            </button>

            {menuOpen && (
              <ProfileMenu
                profile={profile}
                theme={theme}
                toggleTheme={toggleTheme}
                onAddAthlete={() => {
                  setMenuOpen(false);
                  setAddAthleteOpen(true);
                }}
                onLogout={() => {
                  setMenuOpen(false);
                  logout();
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Content area */}
      <main className="relative mx-auto max-w-2xl px-5 pb-28 md:pl-56 md:pb-8">
        <Outlet />
      </main>

      {/* Mobile bottom nav */}
      <BottomNav />

      <AddAthleteModal
        open={addAthleteOpen}
        onClose={() => setAddAthleteOpen(false)}
      />
    </div>
  );
}

// Extracted to avoid duplication between mobile header and desktop top bar
function ProfileMenu({
  profile,
  theme,
  toggleTheme,
  onAddAthlete,
  onLogout,
}: {
  profile: { name?: string; email?: string } | null;
  theme: string;
  toggleTheme: () => void;
  onAddAthlete: () => void;
  onLogout: () => void;
}) {
  return (
    <div className="absolute right-0 top-full mt-2 w-60 rounded-2xl border border-border bg-card p-2 shadow-xl shadow-foreground/5">
      <div className="px-3 py-3">
        <p className="text-sm font-semibold text-foreground">
          {profile?.name ?? "Coach"}
        </p>
        <p className="text-xs text-muted-foreground">{profile?.email}</p>
      </div>

      <div className="mx-2 h-px bg-border" />

      <button
        onClick={onAddAthlete}
        className="mt-1 flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-foreground transition-colors hover:bg-secondary"
      >
        <Plus className="h-4 w-4" />
        Add Athlete
      </button>

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