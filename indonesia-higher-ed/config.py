"""Every editable parameter for the pipeline lives here."""
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"          # caches + per-stage outputs (git-ignored)
OUTPUT = ROOT / "output"

# ---- Stage 1: source (Kemdiktisaintek open-data portal, 2025) ----------------
PT_URL = "https://data.kemdiktisaintek.go.id/download/datasets/6"      # Perguruan Tinggi.xlsx
PT_COLS = {"npsn": "npsn", "name": "nama_pt", "city_raw": "Kabupaten_pt", "province_raw": "provinsi_pt"}
OFFICIAL_TOTAL = 4416                 # 2025 official; PDDikti homepage now shows 4621
OFFICIAL_TOTAL_LABEL = "4,416 (2025 official total)"
COUNT_TOLERANCE = 0.03                # widened from 2% by user decision (source has 4,303 = -2.56%)
PLACEHOLDER_CITIES = {"lainnya", "-", ""}   # source values that mean "no city"
CITY_RESEARCH = ROOT / "city_research.csv"  # researched city per NPSN for placeholder rows, with evidence
UNKNOWN_CITY = "Jakarta (City Unknown)"    # user decision: kept rows whose city no source gives; beach = "unknown"

# ---- Stage 2: age filter -----------------------------------------------------
PRODI_URL = "https://data.kemdiktisaintek.go.id/download/datasets/5"   # Program Studi.xlsx
PRODI_COLS = {"npsn": "npsn", "level": "nm_jenj_didik"}
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
    (r"^kota\.?\s+", "Kota "),
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
CITY_ALIASES = {                       # cleaned source name -> current official name (typos and renames)
    "Kabupaten Bolaang Mongondaw": "Kabupaten Bolaang Mongondow",
    "Kabupaten Humbang Hasudutan": "Kabupaten Humbang Hasundutan",
    "Kabupaten Kep. Sangihe": "Kabupaten Kepulauan Sangihe",
    "Kabupaten Kepulauan Morotai": "Kabupaten Pulau Morotai",
    "Kabupaten Kepulauan Sitaro": "Kabupaten Kepulauan Siau Tagulandang Biaro",
    "Kabupaten Lima Puluh Koto": "Kabupaten Lima Puluh Kota",
    "Kabupaten Maluku Tenggara Barat": "Kabupaten Kepulauan Tanimbar",    # renamed 2019
    "Kabupaten Mamuju Utara": "Kabupaten Pasangkayu",                     # renamed 2017
    "Kabupaten Marowali": "Kabupaten Morowali",
    "Kabupaten Nagakeo": "Kabupaten Nagekeo",
    "Kabupaten Pasawaran": "Kabupaten Pesawaran",
    "Kabupaten Pasir": "Kabupaten Paser",                                 # renamed 2007
    "Kabupaten Polewali Mamasa": "Kabupaten Polewali Mandar",             # renamed 2005
    "Kabupaten Pontianak": "Kabupaten Mempawah",                          # renamed 2014
    "Kabupaten Sabussalam": "Kota Subulussalam",
    "Kabupaten Sawahlunto/ Sijunjung": "Kabupaten Sijunjung",             # renamed 2008
    "Kabupaten Selayar": "Kabupaten Kepulauan Selayar",
    "Kabupaten Sungai Penuh": "Kota Sungai Penuh",
    "Kabupaten Tenggamus": "Kabupaten Tanggamus",
    "Kabupaten Toba Samosir": "Kabupaten Toba",                           # renamed 2020
    "Kabupaten Yapen Waropen": "Kabupaten Kepulauan Yapen",
    "Kota Padang Sidempuan": "Kota Padangsidimpuan",
}

# ---- Stage 4: beach ----------------------------------------------------------
OSM_PBF_URL = "https://download.openstreetmap.fr/extracts/asia/indonesia-latest.osm.pbf"
OSM_ADMIN_LEVEL_CITY = "5"             # Indonesia: 4 = province, 5 = kabupaten/kota
OSM_ADMIN_LEVEL_PROVINCE = "4"
OSM_NAME_TAGS = ["name", "name:id", "official_name", "alt_name"]
OSM_RELATION_OVERRIDES = {             # "City|Province" -> OSM relation id, where OSM names are wrong
    "Kota Langsa|Aceh": 8922311,       # OSM official_name says "Kabupaten Langsa"; Langsa is a Kota
}
OSM_OPEN_BOUNDARIES = {7830591: "5"}   # relation id -> admin_level; ring not closed in OSM (Rokan Hilir), outline rebuilt
OPEN_BOUNDARY_HULL_RATIO = 0.05        # concave-hull tightness used when the open ring cannot be polygonized
COASTLINE_MAX_M = 300                  # sea beach = within this distance of natural=coastline
METERS_PER_DEGREE = 111_320            # Indonesia straddles the equator, so degrees ~ metres / this
EXCLUDED_SURFACES = {"mud", "rock", "rocks", "stone", "bare_rock", "concrete"}
BEACH_NAME_PREFIX = "pantai "          # Indonesian for "beach"; used with the tourism/leisure tags below
BEACH_TOURISM_VALUES = {"attraction", "viewpoint", "picnic_site"}   # named "Pantai ..." with these = recreational beach
BEACH_LEISURE_VALUES = {"beach_resort"}
BEACH_NAMES_LISTED = 3
SPOTCHECK_SIZE = 20
SPOTCHECK_MIN_AGREE = 19
SPOTCHECK_SEED = 2025
SPOTCHECK_FILE = ROOT / "spotcheck_web.csv"   # second source: city, web_beach (yes/no), evidence (URL + named beach)

# ---- Stage 5: deliver ----------------------------------------------------------
WORKBOOK = OUTPUT / "indonesia_higher_ed.xlsx"
