import React from "react";
import { useEvents } from "../../hooks/useEvents";

interface EventSelectorProps {
  selectedEvent: string;
  onChange: (value: string) => void;
}

const EventSelector: React.FC<EventSelectorProps> = ({
  selectedEvent,
  onChange,
}) => {
  const { events, loading, error } = useEvents();

  if (loading) return <p>Loading events...</p>;
  if (error) return <p>Error loading events: {error}</p>;

  return (
    <div>
      <label htmlFor="event-select">Select Event:</label>
      <select
        id="event-select"
        value={selectedEvent}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">-- Choose an event --</option>

        {events.map((event) => (
          <option key={event.value} value={event.value}>
            {event.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default EventSelector;
