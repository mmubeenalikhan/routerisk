import math
from datetime import timedelta

from .clients.routing import fetch_routes
from .clients.weather import fetch_hourly
from .engine.checkpoints import haversine_mi, place_checkpoints, road_segments
from .engine.heatmap import CELL_DEG, hourly_risk, squares_along
from .engine.ranking import average_risk, miles_by_risk, rank_routes
from .engine.risk import NAMES, checkpoint_risk, cm_to_in, kmh_to_mph, mm_to_in

MAX_TRIP_KM = 1500 # Valhalla server restriction(in straight-line)
KM_PER_MI = 1.609344
HEATMAP_HOURS = 48
ALL_BLOCKED_MESSAGE = "No safe route at this departure time. Try leaving later."

def plan_trip(origin, destination, departure, load_lb, interval_mi):
  check_trip_length(origin, destination)

  routes = fetch_routes(origin, destination)
  for route in routes:
    route["checkpoints"] = place_checkpoints(route["points"], route["maneuvers"], interval_mi)

  add_checkpoint_weather(routes, departure, load_lb)
  for route in routes:
    add_risk_summary(route)
  all_blocked = rank_routes(routes)

  return {
    "departure": utc_iso(departure),
    "load_lb": load_lb,
    "interval_mi": interval_mi,
    "recommended_route_id": None if all_blocked else routes[0]["id"],
    "all_blocked": all_blocked,
    "message": ALL_BLOCKED_MESSAGE if all_blocked else None,
    "routes": [route_response(route, departure) for route in routes],
    "heatmap": build_heatmap(routes, departure, load_lb),
    "warnings": route_count_warnings(routes),
  }

def check_trip_length(origin, destination):
  km = haversine_mi((origin["lat"], origin["lon"]), (destination["lat"], destination["lon"])) * KM_PER_MI
  if km > MAX_TRIP_KM:
    raise ValueError(f"Trips over 1,500 KM are not supported yet. (Given is {km:,.0f} KM in a straight-line).")

def add_checkpoint_weather(routes, departure, load_lb):
  checkpoints = [cp for route in routes for cp in route["checkpoints"]]
  for cp in checkpoints:
    cp["eta"] = departure + timedelta(seconds=cp["elapsed_s"])

  start = departure.replace(minute=0, second=0, microsecond=0)
  end = max(cp["eta"] for cp in checkpoints) + timedelta(hours=1)
  hourly = fetch_hourly([(cp["lat"], cp["lon"]) for cp in checkpoints], start, end)

  for cp, weather in zip(checkpoints, hourly):
    i = math.ceil((cp["eta"] - start).total_seconds() / 3600)
    cp["wind_mph"] = kmh_to_mph(weather["wind_speed_10m"][i])
    cp["rain_in_hr"] = mm_to_in(weather["rain"][i] + weather["showers"][i])
    cp["snow_in_hr"] = cm_to_in(weather["snowfall"][i])
    cp["risk_level"] = checkpoint_risk(cp["wind_mph"], cp["rain_in_hr"], cp["snow_in_hr"], load_lb)
    cp["risk"] = NAMES[cp["risk_level"]]

def add_risk_summary(route):
  miles_and_risk = [(cp["mile"], cp["risk_level"]) for cp in route["checkpoints"]]
  route["risk_miles"] = miles_by_risk(miles_and_risk)
  route["avg_risk"] = average_risk(route["risk_miles"])

def build_heatmap(routes, departure, load_lb):
  squares = squares_along([point for route in routes for point in route["points"]])
  start = departure.replace(minute=0, second=0, microsecond=0)
  hourly = fetch_hourly(squares, start, start + timedelta(hours=HEATMAP_HOURS))
  return {
    "cell_deg": CELL_DEG,
    "start": utc_iso(start),
    "hours": HEATMAP_HOURS + 1,
    "cells": [
      {"lat": lat, "lon": lon, "risk": hourly_risk(weather, load_lb)}
        for (lat, lon), weather in zip(squares, hourly)
    ],
  }

def route_response(route, departure):
  return {
    "id": route["id"],
    "rank": route["rank"],
    "status": route["status"],
    "distance_mi": route["distance_mi"],
    "duration_s": route["duration_s"],
    "arrival": utc_iso(departure + timedelta(seconds=route["duration_s"])),
    "risk_miles": route["risk_miles"],
    "avg_risk": round(route["avg_risk"], 2),
    "segments": road_segments(route["points"], route["checkpoints"]),
    "checkpoints": [checkpoint_response(cp) for cp in route["checkpoints"]],
  }

def checkpoint_response(cp):
  return {
    "mile": cp["mile"],
    "lat": round(cp["lat"], 5),
    "lon": round(cp["lon"], 5),
    "eta": utc_iso(cp["eta"]),
    "elapsed_h": round(cp["elapsed_s"] / 3600, 2),
    "wind_mph": cp["wind_mph"],
    "rain_in_hr": cp["rain_in_hr"],
    "snow_in_hr": cp["snow_in_hr"],
    "risk": cp["risk"],
  }

def route_count_warnings(routes):
  if len(routes) == 3:
    return []
  return [f"Only {len(routes)} distinct route{'s' if len(routes) > 1 else ''} found for this trip."]

def utc_iso(dt):
  return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
