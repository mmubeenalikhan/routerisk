import time

import requests
from django.core.cache import cache

URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "RouteRisk/0.1"}
CACHE_SECONDS = 30 * 24 * 60 * 60

def geocode(name):
  key = "geo:" + name.strip().lower().replace(" ", "_")
  place = cache.get(key)
  if place:
    return place
  params = {"q": name, "format": "json", "limit": 1}
  results = requests.get(URL, params=params, headers=HEADERS, timeout=30).json()
  if not results:
    raise ValueError(f"Place not found: {name}")
  place = {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}
  cache.set(key, place, CACHE_SECONDS)
  time.sleep(1) # Nominatim: 1 request per second
  return place
