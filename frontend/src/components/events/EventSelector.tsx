import React from "react";
import { useEvents } from "../../hooks/useEvents";
import type { EventTypeEnum } from "../../types/event.types";

interface EventSelectorProps {
  value: EventTypeEnum | null;
  onChange: (event: EventTypeEnum | null) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const EventSelector: React.FC<EventSelectorProps> = ({
  value,
  onChange,
  placeholder = "Select an event...",
  disabled = false,
  className = "",
}) => {
  const events = useEvents();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = e.target.value;
    onChange(selected ? (selected as EventTypeEnum) : null);
  };

  return (
    <div className={`event-selector ${className}`}>
      <select
        style={{ color: "black", backgroundColor: "white" }}
        className="event-selector__select"
        value={value ?? ""}
        onChange={handleChange}
        disabled={disabled}
        aria-label="Select event type"
      >
        <option value="" disabled style={{ color: "black" }}>
          {placeholder}
        </option>
        {events.map((event) => (
          <option key={event.value} value={event.value} style={{ color: "black" }}>
            {event.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default EventSelector;
