import { NavLink } from "react-router-dom";
import { Home, Circle, Clock } from "lucide-react";

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/record", icon: Circle, label: "Record" },
  { to: "/history", icon: Clock, label: "History" },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card">
      <div className="mx-auto flex max-w-lg items-center justify-around py-1.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `relative flex flex-col items-center gap-0.5 rounded-xl px-5 py-2 text-[11px] font-semibold tracking-wide transition-colors ${
                isActive
                  ? "text-foreground"
                  : "text-muted-foreground"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span
                    className="absolute inset-0 rounded-xl opacity-[0.08]"
                    style={{ backgroundColor: "hsl(var(--primary))" }}
                  />
                )}
                <Icon className="relative h-5 w-5" strokeWidth={isActive ? 2.2 : 1.8} />
                <span className="relative">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}