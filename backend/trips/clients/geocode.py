import requests
from django.core.cache import cache

# Photon (komoot): the public Nominatim server rejects requests from shared cloud hosts such as Render.
URL = "https://photon.komoot.io/api/"
HEADERS = {"User-Agent": "RouteRisk/0.1"}
CACHE_SECONDS = 30 * 24 * 60 * 60

def geocode(name):
  key = "geo:" + name.strip().lower().replace(" ", "_")
  place = cache.get(key)
  if place:
    return place
  params = {"q": name, "limit": 1, "osm_tag": "place"}  # towns and cities only
  response = requests.get(URL, params=params, headers=HEADERS, timeout=30)
  response.raise_for_status()
  features = response.json()["features"]
  if not features:
    raise ValueError(f"Place not found: {name}")
  lon, lat = features[0]["geometry"]["coordinates"]  # GeoJSON order is [lon, lat]
  place = {"lat": lat, "lon": lon}
  cache.set(key, place, CACHE_SECONDS)
  return place
