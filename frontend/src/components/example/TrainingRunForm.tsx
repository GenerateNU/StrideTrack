import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ExampleRunCreate as TrainingRunCreate } from "@/types";

interface TrainingRunFormProps {
  initialData?: TrainingRunCreate;
  onSubmit: (data: TrainingRunCreate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  submitLabel?: string;
}

export function TrainingRunForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  submitLabel = "Create",
}: TrainingRunFormProps) {
  const [formData, setFormData] = useState<TrainingRunCreate>(
    initialData ?? {
      athlete_name: "",
      distance_meters: 0,
      duration_seconds: 0,
      avg_ground_contact_time_ms: null,
    }
  );

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="athlete_name">Athlete Name</Label>
        <Input
          id="athlete_name"
          value={formData.athlete_name}
          onChange={(e) =>
            setFormData({ ...formData, athlete_name: e.target.value })
          }
          required
          placeholder="Enter athlete name"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="distance_meters">Distance (meters)</Label>
        <Input
          id="distance_meters"
          type="number"
          value={formData.distance_meters || ""}
          onChange={(e) =>
            setFormData({
              ...formData,
              distance_meters: Number(e.target.value) || 0,
            })
          }
          required
          min="1"
          placeholder="Enter distance in meters"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="duration_seconds">Duration (seconds)</Label>
        <Input
          id="duration_seconds"
          type="number"
          step="0.1"
          value={formData.duration_seconds || ""}
          onChange={(e) =>
            setFormData({
              ...formData,
              duration_seconds: Number(e.target.value) || 0,
            })
          }
          required
          min="0.1"
          placeholder="Enter duration in seconds"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="avg_ground_contact_time_ms">
          Avg Ground Contact Time (ms){" "}
          <span className="text-muted-foreground">(optional)</span>
        </Label>
        <Input
          id="avg_ground_contact_time_ms"
          type="number"
          step="0.1"
          value={formData.avg_ground_contact_time_ms ?? ""}
          onChange={(e) =>
            setFormData({
              ...formData,
              avg_ground_contact_time_ms: e.target.value
                ? Number(e.target.value)
                : null,
            })
          }
          placeholder="Enter ground contact time in milliseconds"
        />
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : submitLabel}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
