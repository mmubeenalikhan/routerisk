import polyline
import requests

URL = "https://valhalla1.openstreetmap.de/route"
HEADERS = {"X-Client-Id": "routerisk", "User-Agent": "RouteRisk/0.1"}

def fetch_routes(origin, destination):
  body = {
    "locations": [
      {"lat": origin["lat"], "lon": origin["lon"]},
      {"lat": destination["lat"], "lon": destination["lon"]}
    ],
    "costing": "auto",
    "alternates": 2,
    "units": "miles",
  }
  data = requests.post(URL, json=body, headers=HEADERS, timeout=60).json()
  if "trip" not in data:
    raise ValueError(f"Routing failed: {data.get('error', 'no route found')}")
  trips = [data["trip"]] + [alternate["trip"] for alternate in data.get("alternates", [])]
  return [_to_route("ABC"[index], trip) for index, trip in enumerate(trips)]

def _to_route(route_id, trip):
  leg = trip["legs"][0]
  return {
    "id": route_id,
    "points": polyline.decode(leg["shape"], 6),  # Valhalla encodes shapes with precision 6, not the usual 5
    "maneuvers": leg["maneuvers"],
    "distance_mi": round(trip["summary"]["length"], 1),
    "duration_s": round(trip["summary"]["time"]),
  }