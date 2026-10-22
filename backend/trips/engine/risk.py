LOW, MODERATE, HIGH, SEVERE, NO_TRAVEL = 1, 2, 3, 4, 5
NAMES = {1: "low", 2: "moderate", 3: "high", 4: "severe", 5: "no_travel"}

def kmh_to_mph(v): return round(v / 1.609344, 2)
def mm_to_in(v):   return round(v / 25.4, 2)
def cm_to_in(v):   return round(v / 2.54, 2)

def wind_risk(mph):
  if mph >= 55: return NO_TRAVEL
  if mph >= 45: return SEVERE
  if mph >= 35: return HIGH
  if mph >= 25: return MODERATE
  return LOW

def rain_risk(in_hr):
  if in_hr > 1.00: return NO_TRAVEL
  if in_hr >= 0.50: return SEVERE
  if in_hr >= 0.25: return HIGH
  if in_hr >= 0.10: return MODERATE
  return LOW

def snow_risk(in_hr):
  if in_hr > 3.0: return NO_TRAVEL
  if in_hr >= 2.0: return SEVERE
  if in_hr >= 1.0: return HIGH
  if in_hr >= 0.5: return MODERATE
  return LOW

def apply_load_rule(level, mph, load_lb):
  if 45 <= mph < 55 and load_lb > 30000: return NO_TRAVEL
  if 35 <= mph < 45 and load_lb > 40000: return SEVERE
  return level

def checkpoint_risk(wind_mph, rain_in_hr, snow_in_hr, load_lb):
  if wind_mph is None or rain_in_hr is None or snow_in_hr is None:
    return HIGH  # missing value is considerred high
  wind = apply_load_rule(wind_risk(wind_mph), wind_mph, load_lb)
  return max(wind, rain_risk(rain_in_hr), snow_risk(snow_in_hr))
