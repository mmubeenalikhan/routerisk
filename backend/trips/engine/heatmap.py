import math

from .risk import checkpoint_risk, cm_to_in, kmh_to_mph, mm_to_in

CELL_DEG = 0.5

def squares_along(route_points):
  half_square = CELL_DEG / 2
  centres = {
    (math.floor(lat / CELL_DEG) * CELL_DEG + half_square, math.floor(lon / CELL_DEG) * CELL_DEG + half_square)
    	for lat, lon in route_points
  }
  return sorted(centres)

def hourly_risk(hourly, load_lb):
  hours = zip(hourly["wind_speed_10m"], hourly["rain"], hourly["showers"], hourly["snowfall"])
  return [
    checkpoint_risk(kmh_to_mph(wind), mm_to_in(rain + showers), cm_to_in(snow), load_lb)
    	for wind, rain, showers, snow in hours
  ]

