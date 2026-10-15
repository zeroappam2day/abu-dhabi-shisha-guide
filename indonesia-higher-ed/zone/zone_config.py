"""All parameters for the priority-zone gap mission (overlay only; never writes outside zone/)."""
from pathlib import Path

ZONE = Path(__file__).resolve().parent
ROOT = ZONE.parent                                   # indonesia-higher-ed/ (read-only)
WORKBOOK = ROOT / "output" / "indonesia_higher_ed.xlsx"
SHEET = "Beach shortlist"
BASELINE = ZONE / "BASELINE.sha256"
BASELINE_COMMIT = "e34937f"

ZONE_LIST = ZONE / "zone_list.csv"                   # the 70 keys + all 18 baseline values
SWIM_V2 = ZONE / "swim_v2.csv"
SAFETY_V2 = ZONE / "safety_v2.csv"
NUMBERS_V2 = ZONE / "numbers_v2.csv"
SPOT_V2 = ZONE / "spotcheck_v2.csv"
WORK = ZONE / "work"                                 # agent batch inputs/outputs
OUTPUT = ZONE / "output"
OUT_XLSX = OUTPUT / "priority_zone.xlsx"
OUT_HTML = OUTPUT / "priority_zone.html"

EXPECTED_ROWS = 70
EXPECTED_ZONES = {"Java": 57, "Bali": 7, "Lampung": 6}
OUTSIDE = "Outside"

SAFETY_WINDOW = ("2026-04-15", "2026-10-15")         # same window as the existing ratings
SAFETY_MIN_SOURCES = 2
SPOT_SEED = 4001
SPOT_SIZE = 20
SPOT_SWIM_MIN_AGREE = 18
SEARCH_BUDGET_PER_TURN = 200
SEARCH_RESERVE = 10

UNVERIFIED = "UNVERIFIED"
CHECKED_VALUES = {"opened", "summary", "none"}
