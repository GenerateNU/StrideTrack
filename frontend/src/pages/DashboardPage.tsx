import { useAuth } from "@/context/auth.context";
import { useState } from "react";
import EventSelector from "@/components/events/EventSelector";

export default function DashboardPage() {
  const { profile, mode, logout } = useAuth();
  const [selectedEvent, setSelectedEvent] = useState("");
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Name: {profile?.name}</p>
      <p>Email: {profile?.email}</p>
      <p>Auth Method: {mode === "google" ? "Google" : "Dev"}</p>
      <hr />
      <h2>Select Event</h2>
      <EventSelector
        selectedEvent={selectedEvent}
        onChange={setSelectedEvent}
      />
      {selectedEvent && <p>Selected event enum: {selectedEvent}</p>}
      <br />
      <button onClick={logout}>Sign out</button>
    </div>
  );
}
