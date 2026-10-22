from datetime import datetime, timedelta, timezone

import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .clients.geocode import geocode
from .pipeline import plan_trip

MAX_DAYS_AHEAD = 7 # Departure + 48H
MAX_LOAD_LB = 80000
INTERVALS_MI = (10, 25, 50)
SERVICE_DOWN = "A routing or weather service didn't respond. Please try again in a minute."


@api_view(["GET"])
def health(request):
  return Response({"ok": True})


@api_view(["POST"])
def plan(request):
  try:
    return Response(plan_trip(*parse_plan_request(request.data)))
  except ValueError as error:
    return Response({"error": str(error)}, status=400)
  except requests.RequestException:
    return Response({"error": SERVICE_DOWN}, status=502)


def parse_place(value, field):
  if isinstance(value, dict):
    try:
      return {"lat": float(value["lat"]), "lon": float(value["lon"])}
    except (KeyError, TypeError, ValueError):
      raise ValueError(f"The {field} is missing its coordinates.")
  name = str(value or "").strip()
  if not name:
    raise ValueError(f"Enter the {field}.")
  return geocode(name)


def parse_plan_request(body):
  load_lb = int(body.get("load_lb", 0))
  if not 1 <= load_lb <= MAX_LOAD_LB:
    raise ValueError("Load must be between 1 and 80,000 lb.")

  interval_mi = int(body.get("interval_mi", 25))
  if interval_mi not in INTERVALS_MI:
    raise ValueError("Checkpoint interval must be 10, 25 or 50 miles.")

  departure = parse_departure(body.get("departure", ""))

  origin = parse_place(body.get("origin"), "origin")
  destination = parse_place(body.get("destination"), "destination")
  return origin, destination, departure, load_lb, interval_mi


def parse_departure(value):
  departure = datetime.fromisoformat(value).astimezone(timezone.utc).replace(tzinfo=None)
  now = datetime.now(timezone.utc).replace(tzinfo=None)
  if not now - timedelta(hours=1) <= departure <= now + timedelta(days=MAX_DAYS_AHEAD):
    raise ValueError("Departure must be between now and 7 days ahead.")
  return departure
