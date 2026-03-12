import { useState, useRef, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";
import { UserCircle, LogOut, Plus } from "lucide-react";
import { useAuth } from "@/context/auth.context";
import { AddAthleteModal } from "@/components/athletes/AddAthleteModal";
import logo from "@/assets/stridetrack-logo.png";

export function AppLayout() {
  const { logout, profile } = useAuth();
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
        className="pointer-events-none absolute left-1/2 top-0 h-[300px] w-[500px] -translate-x-1/2 rounded-full opacity-[0.06] blur-[100px]"
        style={{
          background:
            "radial-gradient(circle, hsl(var(--primary)) 0%, transparent 70%)",
        }}
      />

      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card/95 px-5 py-4 backdrop-blur-sm">
        <img src={logo} alt="StrideTrack" className="h-9 w-auto" />
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-muted-foreground transition-colors"
          >
            <UserCircle className="h-5 w-5" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-2 w-60 rounded-2xl border border-border bg-card p-2 shadow-xl shadow-foreground/5">
              <div className="px-3 py-3">
                <p className="text-sm font-semibold text-foreground">
                  {profile?.name ?? "Coach"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {profile?.email}
                </p>
              </div>

              <div className="mx-2 h-px bg-border" />

              <button
                onClick={() => {
                  setMenuOpen(false);
                  setAddAthleteOpen(true);
                }}
                className="mt-1 flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-foreground transition-colors hover:bg-secondary"
              >
                <Plus className="h-4 w-4" />
                Add Athlete
              </button>

              <button
                onClick={() => {
                  setMenuOpen(false);
                  logout();
                }}
                className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm text-destructive transition-colors hover:bg-secondary"
              >
                <LogOut className="h-4 w-4" />
                Log Out
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="relative mx-auto max-w-lg px-5 pb-24">
        <Outlet />
      </main>

      <BottomNav />
      <AddAthleteModal
        open={addAthleteOpen}
        onClose={() => setAddAthleteOpen(false)}
      />
    </div>
  );
}