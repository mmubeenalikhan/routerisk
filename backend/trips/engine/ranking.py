from .risk import NAMES

def miles_by_risk(miles_and_risk):
  miles = {name: 0.0 for name in NAMES.values()}
  for (start_mile, risk_level), (end_mile, _) in zip(miles_and_risk, miles_and_risk[1:]):
    miles[NAMES[risk_level]] += end_mile - start_mile
  return {name: round(total, 1) for name, total in miles.items()}

def average_risk(risk_miles):
  weighted_total = sum(level * risk_miles[name] for level, name in NAMES.items())
  route_miles = sum(risk_miles.values())
  return weighted_total / route_miles

def safety_order(route):
  miles = route["risk_miles"]
  return (
    round(miles["no_travel"]),
    round(miles["severe"]),
    round(miles["high"]),
    round(route["avg_risk"] / 0.05), # noise fix
    route["duration_s"],
  )

def rank_routes(routes):
  routes.sort(key=safety_order)
  for rank, route in enumerate(routes, 1):
    route["rank"] = rank
    route["status"] = "blocked" if round(route["risk_miles"]["no_travel"]) else "ok"

  best_route = routes[0]
  if best_route["status"] == "blocked":
    return True
  best_route["status"] = "recommended"
  return False
