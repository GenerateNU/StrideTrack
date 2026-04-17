import { useState } from "react";
import { X } from "lucide-react";
import { useUpdateAthlete } from "@/hooks/useAthletes.hooks";
import type { Athlete } from "@/types/athlete.types";

interface EditAthleteModalProps {
  open: boolean;
  onClose: () => void;
  athlete: Athlete;
}

export function EditAthleteModal({
  open,
  onClose,
  athlete,
}: EditAthleteModalProps) {
  const { updateAthlete, updateAthleteIsLoading, updateAthleteError } =
    useUpdateAthlete();
  const [name, setName] = useState(athlete.name);
  const [heightIn, setHeightIn] = useState(athlete.height_in?.toString() ?? "");
  const [weightLbs, setWeightLbs] = useState(
    athlete.weight_lbs?.toString() ?? ""
  );
  const [gender, setGender] = useState<"male" | "female" | "">(
    athlete.gender ?? ""
  );

  const handleSubmit = async () => {
    if (!name.trim()) return;
    try {
      await updateAthlete({
        athleteId: athlete.athlete_id,
        payload: {
          name: name.trim(),
          height_in: heightIn ? parseFloat(heightIn) : null,
          weight_lbs: weightLbs ? parseFloat(weightLbs) : null,
          gender: gender || null,
        },
      });
      onClose();
    } catch {
      // error captured in updateAthleteError
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-foreground/20 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative z-10 mx-4 w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground">Edit Athlete</h2>
          <button
            onClick={onClose}
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
              className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Gender
            </label>
            <select
              value={gender}
              onChange={(e) =>
                setGender(e.target.value as "male" | "female" | "")
              }
              className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm text-foreground focus:outline-none"
            >
              <option value="">Not set</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
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
          disabled={!name.trim() || updateAthleteIsLoading}
          className="mt-6 w-full rounded-xl py-3.5 text-sm font-semibold transition-all disabled:opacity-40"
          style={{
            backgroundColor: "hsl(var(--primary))",
            color: "hsl(var(--primary-foreground))",
          }}
        >
          {updateAthleteIsLoading ? "Saving..." : "Save Changes"}
        </button>

        {updateAthleteError && (
          <p className="mt-2 text-center text-xs text-destructive">
            Failed to update athlete. Please try again.
          </p>
        )}
      </div>
    </div>
  );
}
