import math

EARTH_RADIUS_MI = 3958.8
ROAD_POINT_STEP = 4

def haversine_mi(from_point, to_point):
  from_lat, from_lon, to_lat, to_lon = map(math.radians, (*from_point, *to_point))
  haversine = (math.sin((to_lat - from_lat) / 2) ** 2
               + math.cos(from_lat) * math.cos(to_lat) * math.sin((to_lon - from_lon) / 2) ** 2)
  return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(haversine))

def miles_along_road(road_points):
  miles_so_far = [0.0]
  for index in range(1, len(road_points)):
    miles_so_far.append(miles_so_far[-1] + haversine_mi(road_points[index - 1], road_points[index]))
  return miles_so_far

def seconds_along_road(road_points, miles_so_far, maneuvers):
  seconds_so_far = [0.0] * len(road_points)
  for maneuver in maneuvers:
    maneuver_start, maneuver_end = maneuver["begin_shape_index"], maneuver["end_shape_index"]
    maneuver_miles = miles_so_far[maneuver_end] - miles_so_far[maneuver_start]
    for index in range(maneuver_start + 1, maneuver_end + 1):
      gap_miles = miles_so_far[index] - miles_so_far[index - 1]
      share_of_maneuver = gap_miles / maneuver_miles if maneuver_miles > 0 else 0
      seconds_so_far[index] = seconds_so_far[index - 1] + maneuver["time"] * share_of_maneuver
  return seconds_so_far

def checkpoint_miles(total_miles, interval_mi):
  miles = [count * interval_mi for count in range(int(total_miles // interval_mi) + 1)]
  if miles[-1] < total_miles:
    miles.append(total_miles)
  return miles

def make_checkpoints(road_points, miles_so_far, seconds_so_far, interval_mi):
  checkpoints = []
  before = 0
  last_possible_before = len(road_points) - 2
  for checkpoint_mile in checkpoint_miles(miles_so_far[-1], interval_mi):
    while before < last_possible_before and miles_so_far[before + 1] < checkpoint_mile:
      before += 1

    after = before + 1
    gap_miles = miles_so_far[after] - miles_so_far[before]
    fraction = (checkpoint_mile - miles_so_far[before]) / gap_miles if gap_miles > 0 else 0
    (before_lat, before_lon), (after_lat, after_lon) = road_points[before], road_points[after]
    before_seconds, after_seconds = seconds_so_far[before], seconds_so_far[after]
    checkpoints.append({
      "mile": round(checkpoint_mile, 1),
      "lat": before_lat + fraction * (after_lat - before_lat),
      "lon": before_lon + fraction * (after_lon - before_lon),
      "elapsed_s": before_seconds + fraction * (after_seconds - before_seconds),
      "road_point_index": before,
    })
  return checkpoints

def place_checkpoints(road_points, maneuvers, interval_mi):
  miles_so_far = miles_along_road(road_points)
  seconds_so_far = seconds_along_road(road_points, miles_so_far, maneuvers)
  return make_checkpoints(road_points, miles_so_far, seconds_so_far, interval_mi)

def road_segments(road_points, checkpoints):
  segments = []
  for this_checkpoint, next_checkpoint in zip(checkpoints, checkpoints[1:]):
    from_index, to_index = this_checkpoint["road_point_index"] + 1, next_checkpoint["road_point_index"] + 1
    road_between = road_points[from_index:to_index:ROAD_POINT_STEP]
    path = [(this_checkpoint["lat"], this_checkpoint["lon"]), *road_between,
            (next_checkpoint["lat"], next_checkpoint["lon"])]
    segments.append({"risk": this_checkpoint["risk"], "path": [(round(lat, 5), round(lon, 5)) for lat, lon in path]})
  return segments