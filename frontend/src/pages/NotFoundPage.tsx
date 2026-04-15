import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <h1 className="text-4xl font-bold text-foreground">404</h1>
      <p className="text-sm text-muted-foreground">Page not found.</p>
      <button
        onClick={() => navigate("/")}
        className="mt-2 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to home
      </button>
    </div>
  );
}
