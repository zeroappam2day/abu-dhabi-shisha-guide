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

# Reviewer overrides applied at merge (agent output files stay untouched). key -> (new value, reason)
SWIM_OVERRIDES = {
    ("Kota Serang", "Banten"): ("Unverified", "only one beach (Pantai Gope) shown non-sand; No needs all shores non-sand or a ban"),
}
SAFETY_OVERRIDES = {
    ("Kabupaten Situbondo", "Jawa Timur"): ("No rating: <2 dated sources found",
                                            "both sources report the same 2026-06-30 police press conference (not independent)"),
}

# Range bands for the poverty / unemployment filters. Lower bound inclusive, upper exclusive; None = open.
# Descriptors are relative to the national rate (opened sources below). Non-numeric values -> BAND_MISSING.
NATIONAL_POVERTY = (8.47, "BPS P0 March 2025 - https://finance.detik.com/berita-ekonomi-bisnis/d-8028465/bps-angka-kemiskinan-ri-terendah-dalam-2-dekade/amp")
NATIONAL_UNEMPLOYMENT = (4.85, "BPS TPT August 2025 - https://www.jawapos.com/nasional/2511050416/bps-proporsi-pekerja-formal-meningkat-tingkat-pengangguran-terbuka-turun")
POVERTY_BANDS = [            # (lo, hi, descriptor); national 8.47%
    (None, 5, "Very low"), (5, 8, "Below national"), (8, 10, "Near national"),
    (10, 13, "Above national"), (13, None, "High"),
]
UNEMPLOYMENT_BANDS = [       # national 4.85%
    (None, 3, "Very low"), (3, 4.5, "Below national"), (4.5, 5.5, "Near national"),
    (5.5, 7, "Above national"), (7, None, "High"),
]
BAND_MISSING = "Unverified"
