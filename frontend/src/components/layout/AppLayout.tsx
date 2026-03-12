import { useState, useRef, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";
import { UserCircle, LogOut, Plus } from "lucide-react";
import { useAuth } from "@/context/auth.context";

export function AppLayout() {
  const { logout, profile } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
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
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card px-4 py-3">
        <h1 className="text-lg font-bold tracking-tight">StrideTrack</h1>
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="rounded-full p-1.5 text-muted-foreground transition-colors"
          >
            <UserCircle className="h-6 w-6" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-border bg-card p-2 shadow-lg">
              <div className="px-3 py-2">
                <p className="text-sm font-semibold text-foreground">
                  {profile?.name ?? "Coach"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {profile?.email}
                </p>
              </div>

              <div className="my-1 h-px bg-border" />

              <button
                onClick={() => {
                  setMenuOpen(false);
                }}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-foreground transition-colors hover:bg-secondary"
              >
                <Plus className="h-4 w-4" />
                Add Athlete
              </button>

              <button
                onClick={() => {
                  setMenuOpen(false);
                  logout();
                }}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-destructive transition-colors hover:bg-secondary"
              >
                <LogOut className="h-4 w-4" />
                Log Out
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 pb-24">
        <Outlet />
      </main>

      <BottomNav />
    </div>
  );
}