import { Outlet } from "react-router-dom";
import { BottomNav } from "./BottomNav";
import { UserCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function AppLayout() {
  const { signOut } = useAuth();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card/95 px-4 py-3 backdrop-blur-sm">
        <h1 className="text-lg font-bold tracking-tight">StrideTrack</h1>
        <button
          onClick={signOut}
          className="rounded-full p-1.5 text-muted-foreground transition-colors"
        >
          <UserCircle className="h-6 w-6" />
        </button>
      </header>

      <main className="mx-auto max-w-lg px-4 pb-24">
        <Outlet />
      </main>

      <BottomNav />
    </div>
  );
}