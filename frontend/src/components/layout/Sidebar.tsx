import { useState, useRef, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { Home, Circle, Clock, UserCircle } from "lucide-react";
import { useAuth } from "@/context/auth.context";
import { useTheme } from "@/hooks/useTheme";
import { ProfileMenu } from "./ProfileMenu";
import { AddAthleteModal } from "@/components/athletes/AddAthleteModal";
import logo from "@/assets/stridetrack-logo.png";

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/record", icon: Circle, label: "Record" },
  { to: "/history", icon: Clock, label: "History" },
];

export function Sidebar() {
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
    <>
      <aside className="fixed left-0 top-0 hidden h-screen w-56 flex-col border-r border-border bg-card md:flex">
        <div className="px-5 py-6">
          <img src={logo} alt="StrideTrack" className="h-11 w-auto" />
        </div>

        <nav className="flex-1 px-3 py-2">
          <div className="space-y-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-secondary text-foreground"
                      : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className="h-[18px] w-[18px]"
                      strokeWidth={isActive ? 2.2 : 1.8}
                    />
                    <span>{label}</span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </nav>

        <div className="relative border-t border-border px-3 py-3" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-muted-foreground transition-colors hover:bg-secondary"
          >
            <UserCircle className="h-5 w-5" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">
                {profile?.name ?? "Coach"}
              </p>
            </div>
          </button>

          {menuOpen && (
            <div className="absolute bottom-full left-2 right-2 mb-2">
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
            </div>
          )}
        </div>
      </aside>

      <AddAthleteModal
        open={addAthleteOpen}
        onClose={() => setAddAthleteOpen(false)}
      />
    </>
  );
}