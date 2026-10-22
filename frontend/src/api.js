const API_URL = import.meta.env.VITE_API_URL ?? "";

const PHOTON_URL = "https://photon.komoot.io/api/";

async function request(path, options) {
  const response = await fetch(API_URL + path, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error ?? `Request failed (${response.status})`);
  return body;
}

function toPlace({ geometry, properties }) {
  const [lon, lat] = geometry.coordinates;
  const label = [properties.name, properties.state, properties.country].filter(Boolean).join(", ");
  return { id: `${properties.osm_type}${properties.osm_id}`, label, kind: properties.osm_value, lat, lon };
}

export const checkHealth = () => request("/api/health");

export async function searchPlaces(text, signal) {
  const query = new URLSearchParams({ q: text, limit: 5, osm_tag: "place" });
  const response = await fetch(`${PHOTON_URL}?${query}`, { signal });
  const { features } = await response.json();
  return features.map(toPlace);
}

export const planTrip = trip =>
  request("/api/trips/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(trip),
  });
