import { X } from "lucide-react";

interface DeleteConfirmModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isLoading?: boolean;
  title: string;
  description: string;
}

export function DeleteConfirmModal({ open, onClose, onConfirm, isLoading, title, description }: DeleteConfirmModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-foreground/20 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 mx-4 w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground">{title}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-muted-foreground transition-colors hover:text-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>

        <p className="text-sm text-muted-foreground">{description}</p>

        <div className="mt-6 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-xl border border-border py-3 text-sm font-semibold text-foreground transition-all hover:bg-secondary"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="flex-1 rounded-xl py-3 text-sm font-semibold text-white transition-all disabled:opacity-40"
            style={{ backgroundColor: "hsl(var(--destructive))" }}
          >
            {isLoading ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
