import { useCreateAthlete } from "@/hooks/useAthletes.hooks";
import { X } from "lucide-react";
import { useState } from "react";

interface AddAthleteModalProps {
  open: boolean;
  onClose: () => void;
}

export function AddAthleteModal({ open, onClose }: AddAthleteModalProps) {
  const { createAthlete, createAthleteIsLoading, createAthleteError } =
    useCreateAthlete();
  const [name, setName] = useState("");
  const [heightIn, setHeightIn] = useState("");
  const [weightLbs, setWeightLbs] = useState("");

  const resetAndClose = () => {
    setName("");
    setHeightIn("");
    setWeightLbs("");
    onClose();
  };

  const handleSubmit = async () => {
    if (!name.trim()) return;
    try {
      await createAthlete({
        name: name.trim(),
        height_in: heightIn ? parseFloat(heightIn) : null,
        weight_lbs: weightLbs ? parseFloat(weightLbs) : null,
      });
      resetAndClose();
    } catch {
      // error is captured in createAthleteError
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute -inset-10 bg-foreground/20"
        onClick={resetAndClose}
      />
      <div className="relative z-10 mx-4 w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground">Add Athlete</h2>
          <button
            onClick={resetAndClose}
            className="rounded-lg p-1 text-muted-foreground transition-colors hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ben Marler"
              className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Height (in)
              </label>
              <input
                type="number"
                value={heightIn}
                onChange={(e) => setHeightIn(e.target.value)}
                placeholder="72"
                className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Weight (lbs)
              </label>
              <input
                type="number"
                value={weightLbs}
                onChange={(e) => setWeightLbs(e.target.value)}
                placeholder="180"
                className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!name.trim() || createAthleteIsLoading}
          className="mt-6 w-full rounded-xl py-3.5 text-sm font-semibold transition-all disabled:opacity-40"
          style={{
            backgroundColor: "hsl(var(--primary))",
            color: "hsl(var(--primary-foreground))",
          }}
        >
          {createAthleteIsLoading ? "Adding..." : "Add Athlete"}
        </button>

        {createAthleteError && (
          <p className="mt-2 text-center text-xs text-destructive">
            Failed to add athlete. Please try again.
          </p>
        )}
      </div>
    </div>
  );
}
