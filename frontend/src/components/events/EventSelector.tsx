import React from "react";
import { useEvents } from "../../hooks/useEvents";
import { ChevronDown } from "lucide-react";
import type { EventTypeEnum } from "../../types/event.types";

interface EventSelectorProps {
  value: EventTypeEnum | null;
  onChange: (event: EventTypeEnum | null) => void;
  placeholder?: string;
  disabled?: boolean;
  label?: string;
}

const EventSelector: React.FC<EventSelectorProps> = ({
  value,
  onChange,
  placeholder = "Select an event",
  disabled = false,
  label = "Event",
}) => {
  const events = useEvents();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = e.target.value;
    onChange(selected ? (selected as EventTypeEnum) : null);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-2">
        {label}
      </label>
      <div className="relative">
        <select
          value={value ?? ""}
          onChange={handleChange}
          disabled={disabled}
          aria-label="Select event type"
          className="w-full appearance-none rounded-xl border border-border bg-card px-4 py-3.5 pr-10 text-sm font-medium text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary disabled:opacity-50"
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {events.map((event) => (
            <option key={event.value} value={event.value}>
              {event.label}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      </div>
    </div>
  );
};

export default EventSelector;
