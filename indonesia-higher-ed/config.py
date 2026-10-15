"""Every editable parameter for the pipeline lives here."""
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"          # caches + per-stage outputs (git-ignored)
OUTPUT = ROOT / "output"

# ---- Stage 1: source (PDDikti API via pddiktipy) ----------------------------
# Gate reference: official total. The live /pt/count value is also logged.
OFFICIAL_TOTAL = 4416                 # 2025 official; PDDikti homepage now shows 4621
OFFICIAL_TOTAL_LABEL = "4,416 (2025 official total)"
COUNT_TOLERANCE = 0.02
KEEP_PT_STATUS = {"aktif"}            # lower-cased status_pt values that count as operating
LIST_PAGE_SIZE = 100
REQUEST_PAUSE_S = 0.3                 # polite delay between PDDikti calls
ENV_CF_CLEARANCE = "PDDIKTI_CF_CLEARANCE"   # cookie from a browser that passed Cloudflare
ENV_USER_AGENT = "PDDIKTI_UA"               # the exact User-Agent of that browser

# ---- Stage 2: age filter -----------------------------------------------------
SEMESTERS = ["20252", "20251", "20242"]   # tried in order until a PT returns programs
KEEP_PRODI_STATUS = {"aktif"}
KEEP_LEVELS = {"S1", "D3", "D4"}
POSTGRAD_LEVELS = {"S2", "S3", "S2T", "S3T", "PROFESI", "SP1", "SP2", "SUBSP"}
LEVEL_ALIASES = {                      # key = upper-case, non-alphanumerics removed
    "DIII": "D3", "DIPLOMAIII": "D3", "DIV": "D4", "DIPLOMAIV": "D4",
    "SARJANATERAPAN": "D4", "SARJANA": "S1",
    "DI": "D1", "DII": "D2", "S2TERAPAN": "S2T", "S3TERAPAN": "S3T",
    "SPESIALIS": "SP1", "SPESIALIS1": "SP1", "SPESIALIS2": "SP2",
}

# ---- Stage 3: clean ----------------------------------------------------------
CITY_PREFIXES = [                      # (regex, replacement), applied in order
    (r"^kota\s+adm(inistrasi|\.)?\s+", "Kota "),
    (r"^kab(upaten|\.)?\s+adm(inistrasi|\.)?\s+", "Kabupaten "),
    (r"^kab(upaten|\.)?\s+", "Kabupaten "),
    (r"^kota\s+", "Kota "),
]
PROVINCE_PREFIXES = [(r"^prov(insi|\.)?\s+", "")]
PROVINCE_ALIASES = {                   # key = lower-case after prefix strip
    "dki jakarta": "DKI Jakarta", "daerah khusus ibukota jakarta": "DKI Jakarta",
    "daerah khusus jakarta": "DKI Jakarta", "d.k.i. jakarta": "DKI Jakarta",
    "di yogyakarta": "DI Yogyakarta", "d.i. yogyakarta": "DI Yogyakarta",
    "daerah istimewa yogyakarta": "DI Yogyakarta",
    "kep. riau": "Kepulauan Riau", "kep. bangka belitung": "Kepulauan Bangka Belitung",
    "bangka belitung": "Kepulauan Bangka Belitung",
    "nanggroe aceh darussalam": "Aceh", "d.i. aceh": "Aceh",
}
CITY_ALIASES = {}                      # "Exact Cleaned Name" -> "Replacement", if a gate asks

# ---- Stage 4: beach ----------------------------------------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_PAUSE_S = 2.0
OSM_ADMIN_LEVEL_CITY = "5"             # Indonesia: 4 = province, 5 = kabupaten/kota
OSM_ADMIN_LEVEL_PROVINCE = "4"
OSM_NAME_TAGS = ["name", "name:id", "official_name", "alt_name"]
OSM_RELATION_OVERRIDES = {}            # "City|Province" -> OSM relation id, if a gate asks
COASTLINE_MAX_M = 300                  # sea beach = within this distance of natural=coastline
EXCLUDED_SURFACES = {"mud", "rock", "rocks", "stone", "bare_rock", "concrete"}
BEACH_NAMES_LISTED = 3
SPOTCHECK_SIZE = 20
SPOTCHECK_MIN_AGREE = 19
SPOTCHECK_SEED = 2025
GEONAMES_URL = "https://download.geonames.org/export/dump/ID.zip"
GEONAMES_BEACH_CODES = {"BCH", "BCHS"}

# ---- Stage 5: deliver ----------------------------------------------------------
WORKBOOK = OUTPUT / "indonesia_higher_ed.xlsx"
