import { useState } from "react";
import { Alert, Button, Stack, TextField, ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";
import PlaceInput from "./PlaceInput";

const INTERVALS_MI = [10, 25, 50];
const MAX_DAYS_AHEAD = 7;
const MAX_TRIP_KM = 1500;
const EARTH_RADIUS_KM = 6371;
const TIME_ZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;

const isPicked = place => typeof place !== "string";
const toRequestPlace = place => (isPicked(place) ? { lat: place.lat, lon: place.lon } : place);

function straightLineKm(a, b) {
  const rad = degrees => (degrees * Math.PI) / 180;
  const h =
    Math.sin(rad(b.lat - a.lat) / 2) ** 2 +
    Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(rad(b.lon - a.lon) / 2) ** 2;
  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(h));
}

function toLocalInputValue(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function departureLimits() {
  const now = new Date();
  const latest = new Date(now.getTime() + MAX_DAYS_AHEAD * 24 * 3600 * 1000);
  const nextFullHour = new Date(now);
  nextFullHour.setHours(now.getHours() + 1, 0, 0, 0);
  return { min: toLocalInputValue(now), max: toLocalInputValue(latest), initial: toLocalInputValue(nextFullHour) };
}

export default function TripForm({ onSubmit, loading }) {
  const [limits] = useState(departureLimits);
  const [origin, setOrigin] = useState("Chicago");
  const [destination, setDestination] = useState("Denver");
  const [departure, setDeparture] = useState(limits.initial);
  const [loadLb, setLoadLb] = useState(42000);
  const [intervalMi, setIntervalMi] = useState(25);

  const [formError, setFormError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const tripKm = isPicked(origin) && isPicked(destination) ? straightLineKm(origin, destination) : 0;
    if (tripKm > MAX_TRIP_KM) {
      const shownKm = Math.round(tripKm).toLocaleString();
      setFormError(`Trips over 1,500 km are not supported yet (this one is ${shownKm} km in a straight line).`);
      return;
    }
    setFormError("");
    onSubmit({
      origin: toRequestPlace(origin),
      destination: toRequestPlace(destination),
      departure: new Date(departure).toISOString(),
      load_lb: Number(loadLb),
      interval_mi: intervalMi,
    });
  }

  return (
    <Stack component="form" spacing={2} onSubmit={handleSubmit}>
      <PlaceInput label="Origin" value={origin} onChange={setOrigin} />

      <PlaceInput label="Destination" value={destination} onChange={setDestination} />
      <TextField
        label="Departure"
        type="datetime-local"
        size="small"
        required
        helperText={TIME_ZONE}
        value={departure}
        onChange={e => setDeparture(e.target.value)}
        slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: limits.min, max: limits.max } }}
      />
      <TextField
        label="Load (lb)"
        type="number"
        size="small"
        required
        value={loadLb}
        onChange={e => setLoadLb(e.target.value)}
        slotProps={{ htmlInput: { min: 1, max: 80000 } }}
      />
      <div>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Weather checkpoint every
        </Typography>
        <ToggleButtonGroup
          exclusive
          fullWidth
          size="small"
          color="primary"
          value={intervalMi}
          onChange={(_, miles) => miles && setIntervalMi(miles)}
        >
          {INTERVALS_MI.map(miles => (
            <ToggleButton key={miles} value={miles}>
              {miles} mi
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </div>
      <Button type="submit" variant="contained" loading={loading}>
        Plan trip
      </Button>
      {formError && <Alert severity="error">{formError}</Alert>}
    </Stack>
  );
}
