import { NavLink } from "react-router-dom";
import { Home, Circle, Clock } from "lucide-react";
import logo from "@/assets/stridetrack-logo.png";

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/record", icon: Circle, label: "Record" },
  { to: "/history", icon: Clock, label: "History" },
];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 hidden h-screen w-56 flex-col border-r border-border bg-card md:flex">
      <div className="px-5 py-6">
        <img src={logo} alt="StrideTrack" className="h-9 w-auto" />
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

      <div className="border-t border-border px-4 py-4">
        <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
          StrideTrack v1.0
        </p>
      </div>
    </aside>
  );
}
