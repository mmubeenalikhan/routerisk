# Boundary tests from the build plan Q7 tables and test checklist
import pytest
from trips.engine.risk import *  # noqa: F403

@pytest.mark.parametrize("mph,exp", [(24.9, LOW), (25, MODERATE), (34.6, MODERATE), (34.9, MODERATE),
  (35, HIGH), (44.9, HIGH), (45, SEVERE), (54.9, SEVERE), (55, NO_TRAVEL)])
def test_wind(mph, exp): assert wind_risk(mph) == exp

@pytest.mark.parametrize("v,exp", [(0.09, LOW), (0.10, MODERATE), (0.25, HIGH), (0.50, SEVERE),
  (1.00, SEVERE), (1.01, NO_TRAVEL)])
def test_rain(v, exp): assert rain_risk(v) == exp

@pytest.mark.parametrize("v,exp", [(0.49, LOW), (0.5, MODERATE), (1.0, HIGH), (2.0, SEVERE),
  (3.0, SEVERE), (3.01, NO_TRAVEL)])
def test_snow(v, exp): assert snow_risk(v) == exp

@pytest.mark.parametrize("mph,load,exp", [(56, 0, NO_TRAVEL), (47, 35000, NO_TRAVEL),
  (47, 30000, SEVERE), (47, 30001, NO_TRAVEL), (38, 42000, SEVERE), (38, 40000, HIGH),
  (38, 40001, SEVERE), (30, 79000, MODERATE)])
def test_load_rules(mph, load, exp): assert checkpoint_risk(mph, 0, 0, load) == exp

def test_rain_beats_wind():       assert checkpoint_risk(10, 0.3, 0, 20000) == HIGH
def test_load_lifts_wind_above(): assert checkpoint_risk(38, 0.05, 0, 42000) == SEVERE
def test_unknown_is_high():       assert checkpoint_risk(None, 0, 0, 20000) == HIGH

# Converted metric values must land in the same band as the exact imperial boundary
@pytest.mark.parametrize("kmh,exp", [(40.2336, MODERATE), (56.32704, HIGH), (72.42048, SEVERE), (88.51392, NO_TRAVEL)])
def test_wind_conversion_boundaries(kmh, exp): assert wind_risk(kmh_to_mph(kmh)) == exp

@pytest.mark.parametrize("mm,exp", [(2.54, MODERATE), (6.35, HIGH), (12.7, SEVERE), (25.4, SEVERE)])
def test_rain_conversion_boundaries(mm, exp): assert rain_risk(mm_to_in(mm)) == exp

@pytest.mark.parametrize("cm,exp", [(1.27, MODERATE), (2.54, HIGH), (5.08, SEVERE), (7.62, SEVERE)])
def test_snow_conversion_boundaries(cm, exp): assert snow_risk(cm_to_in(cm)) == exp
