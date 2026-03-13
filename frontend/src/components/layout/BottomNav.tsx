import { NavLink } from "react-router-dom";
import { Home, Clock } from "lucide-react";

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card">
      <div className="mx-auto flex max-w-lg items-center justify-around py-1.5">
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
          className={({ isActive }) =>
            `relative -mt-5 flex flex-col items-center gap-1 text-[11px] font-semibold tracking-wide transition-colors ${
              isActive ? "text-foreground" : "text-muted-foreground"
            }`
          }
        >
          {({ isActive }) => (
            <>
              <span
                className="flex h-14 w-14 items-center justify-center rounded-full shadow-lg text-primary-foreground"
                style={{
                  background: isActive
                    ? "linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.8))"
                    : "linear-gradient(135deg, hsl(var(--primary) / 0.85), hsl(var(--primary) / 0.65))",
                }}
              >
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <circle cx="12" cy="12" r="8" />
                </svg>
              </span>
              <span>Record</span>
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