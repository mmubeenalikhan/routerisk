import hashlib
import json

import requests
from django.core.cache import cache

URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "RouteRisk/0.1"}
HOURLY = "wind_speed_10m,rain,showers,snowfall"
BATCH_SIZE = 100
CACHE_SECONDS = 30 * 60
HOUR_FORMAT = "%Y-%m-%dT%H:00"

def fetch_hourly(points, start, end):
  hourly = []
  for i in range(0, len(points), BATCH_SIZE):
    hourly += _fetch_batch(points[i:i + BATCH_SIZE], start, end)
  return hourly

def _fetch_batch(points, start, end):
  params = {
    "latitude": ",".join(f"{lat:.3f}" for lat, lon in points),
    "longitude": ",".join(f"{lon:.3f}" for lat, lon in points),
    "hourly": HOURLY,
    "timezone": "UTC",
    "start_hour": start.strftime(HOUR_FORMAT),
    "end_hour": end.strftime(HOUR_FORMAT),
  }
  key = "weather:" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
  result = cache.get(key)
  if result is None:
    response = requests.get(URL, params=params, headers=HEADERS, timeout=60)
    response.raise_for_status()
    result = response.json()
    cache.set(key, result, CACHE_SECONDS)
  if len(points) == 1:
    result = [result]
  return [location["hourly"] for location in result]
