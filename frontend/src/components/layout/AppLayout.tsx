import { useState, useRef, useEffect, Suspense } from "react";
import { Outlet } from "react-router-dom";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { BottomNav } from "./BottomNav";
import { Sidebar } from "./Sidebar";
import { UserCircle } from "lucide-react";
import { useAuth } from "@/context/auth.context";
import { useTheme } from "@/hooks/useTheme.hooks";
import { ProfileMenu } from "./ProfileMenu";
import FlyingFoot from "@/assets/flying_foot.svg?react";
import StrideTrackText from "@/assets/stridetrack_text.svg?react";

export function AppLayout() {
  const { logout, profile } = useAuth();
  const { theme, toggleTheme } = useTheme();
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
    <div className="flex min-h-dvh flex-col bg-background text-foreground">
      <Sidebar />

      {/* Mobile header only */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card/95 px-5 py-4 backdrop-blur-sm md:hidden">
        <FlyingFoot className="h-9 w-auto text-foreground" />
        <StrideTrackText className="absolute left-1/2 -translate-x-1/2 h-7 w-auto" />
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
              onLogout={() => {
                setMenuOpen(false);
                logout();
              }}
            />
          )}
        </div>
      </header>

      <main className="relative w-full flex-1 px-5 pb-20 md:pt-6 md:pl-64 md:pr-8 md:pb-8">
        <Suspense fallback={<QueryLoading />}>
          <Outlet />
        </Suspense>
      </main>

      <BottomNav />
    </div>
  );
}
