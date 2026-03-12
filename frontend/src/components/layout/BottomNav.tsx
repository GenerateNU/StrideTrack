import { NavLink } from "react-router-dom";
import { Home, Circle, Clock } from "lucide-react";

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/record", icon: Circle, label: "Record" },
  { to: "/history", icon: Clock, label: "History" },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-lg items-center justify-around py-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 px-4 py-1 text-xs font-medium transition-colors ${
                isActive ? "text-foreground" : "text-muted-foreground"
              }`
            }
          >
            <Icon className="h-5 w-5" />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}