import { NavLink } from "react-router-dom";
import { Home, Clock } from "lucide-react";

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card pb-[env(safe-area-inset-bottom)] md:hidden">
      <div className="border-t border-border" />
      <div className="mx-auto flex max-w-lg items-end justify-around px-4 pb-2 pt-1">
        {/* Home */}
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `relative flex flex-col items-center gap-0.5 rounded-xl px-5 py-2 text-[11px] font-semibold tracking-wide transition-colors ${
              isActive ? "text-foreground" : "text-muted-foreground"
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
              <Home
                className="relative h-5 w-5"
                strokeWidth={isActive ? 2.2 : 1.8}
              />
              <span className="relative">Home</span>
            </>
          )}
        </NavLink>

        {/* Record — prominent center button */}
        <NavLink
          to="/record"
          className="relative -top-4 flex flex-col items-center gap-1 text-[11px] font-semibold tracking-wide"
        >
          {({ isActive }) => (
            <>
              <span
                className="flex h-14 w-14 items-center justify-center rounded-full text-primary-foreground shadow-lg ring-4 ring-card"
                style={{
                  background: isActive
                    ? "linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.8))"
                    : "linear-gradient(135deg, hsl(var(--primary) / 0.9), hsl(var(--primary) / 0.7))",
                }}
              >
                <div className="h-4 w-4 rounded-full border-[3px] border-primary-foreground" />
              </span>
              <span
                className={
                  isActive ? "text-foreground" : "text-muted-foreground"
                }
              >
                Record
              </span>
            </>
          )}
        </NavLink>

        {/* History */}
        <NavLink
          to="/history"
          className={({ isActive }) =>
            `relative flex flex-col items-center gap-0.5 rounded-xl px-5 py-2 text-[11px] font-semibold tracking-wide transition-colors ${
              isActive ? "text-foreground" : "text-muted-foreground"
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
              <Clock
                className="relative h-5 w-5"
                strokeWidth={isActive ? 2.2 : 1.8}
              />
              <span className="relative">History</span>
            </>
          )}
        </NavLink>
      </div>
    </nav>
  );
}
