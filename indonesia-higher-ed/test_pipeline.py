"""Offline tests: run each stage on mocked PDDikti/Overpass/GeoNames data. `pytest -q`"""
import json
import zipfile

import pytest
from openpyxl import load_workbook

import config as C
import s1_source, s2_age_filter, s3_clean, s4_beach, s5_deliver
from common import clean_city, clean_province, match_key, norm_level, read_rows, write_rows


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "DATA", tmp_path / "data")
    monkeypatch.setattr(C, "OUTPUT", tmp_path / "out")
    monkeypatch.setattr(C, "WORKBOOK", tmp_path / "out" / "wb.xlsx")
    monkeypatch.setattr(C, "REQUEST_PAUSE_S", 0)
    monkeypatch.setattr(C, "OVERPASS_PAUSE_S", 0)


def test_normalizers():
    assert [norm_level(x) for x in ["D-III", "D-IV", "S1", "Sp-1", "S2 Terapan", "Profesi"]] == \
        ["D3", "D4", "S1", "SP1", "S2T", "PROFESI"]
    assert clean_city("Kab.  bandung barat") == "Kabupaten Bandung Barat"
    assert clean_city("KOTA ADM. JAKARTA SELATAN") == "Kota Jakarta Selatan"
    assert clean_city("Kabupaten Administrasi Kepulauan Seribu") == "Kabupaten Kepulauan Seribu"
    assert clean_province("Prov. D.I. Yogyakarta") == "DI Yogyakarta"
    assert clean_province("Daerah Khusus Ibukota Jakarta") == "DKI Jakarta"
    assert match_key("Kab. Bandung") == match_key("Kabupaten Bandung") != match_key("Kota Bandung")


def test_classify():
    c = s2_age_filter.classify
    assert c({"S1", "S2"}) == "keep" and c({"D3"}) == "keep" and c({"D4"}) == "keep"
    assert c({"S2", "S3"}) == "postgrad-only" and c({"D1", "D2"}) == "non-degree" and c(set()) == "no-data"


def fake_pddikti(n_active):
    pts = [{"id_sp": f"id{i}"} for i in range(n_active + 1)]
    details = {f"id{i}": {"nama_pt": f"Univ {i % 3}", "kode_pt": str(i), "kab_kota_pt": "Kab. Badung",
                          "provinsi_pt": "Prov. Bali", "status_pt": "Aktif"} for i in range(n_active)}
    details[f"id{n_active}"] = {"nama_pt": "Closed", "kab_kota_pt": "Kota X", "provinsi_pt": "Bali", "status_pt": "Tutup"}
    progs = {"id0": [{"jenjang_prodi": "S2", "status_prodi": "Aktif"}],
             "id1": [{"jenjang_prodi": "D-I", "status_prodi": "Aktif"}]}

    def get(_client, path):
        if path == "pt/count":
            return {"data": {"jumlah": C.OFFICIAL_TOTAL}}
        if path.startswith("v2/pt/search/filter"):
            off = int(path.split("offset=")[1])
            return {"data": pts[off:off + C.LIST_PAGE_SIZE]}
        if path.startswith("pt/detail/"):
            return {"data": details[path.split("/")[-1]]}
        pt = path.split("/")[2]
        return {"data": progs.get(pt, [{"jenjang_prodi": "S1", "status_prodi": "Aktif"}])}
    return get


def mock_pddikti(monkeypatch, n):
    client = type("Cl", (), {"H": type("H", (), {"parse": staticmethod(str)})})()
    for m in (s1_source, s2_age_filter):
        monkeypatch.setattr(m, "pddikti_get", fake_pddikti(n))
        monkeypatch.setattr(m, "pddikti_client", lambda: client)


def test_s1_gate_fails_on_short_count(monkeypatch):
    mock_pddikti(monkeypatch, 10)
    with pytest.raises(SystemExit, match="Stage 1 gate FAILED"):
        s1_source.main()


def test_end_to_end(monkeypatch):
    n = C.OFFICIAL_TOTAL
    mock_pddikti(monkeypatch, n)
    s1_source.main()
    s2_age_filter.main()
    assert len(read_rows("s1_institutions.csv")) == n                    # closed PT excluded
    kept = read_rows("s2_institutions.csv")
    assert len(kept) == n - 2                                            # S2-only and D1-only dropped
    s3_clean.main()
    rows = read_rows("s3_institutions.csv")
    assert {r["city"] for r in rows} == {"Kabupaten Badung"} and rows[0]["province"] == "Bali"
    assert all(r["duplicate"] == "yes" for r in rows)                    # names repeat in same city

    square = [{"lat": 0, "lon": 0}, {"lat": 0, "lon": 1}, {"lat": 1, "lon": 1}, {"lat": 1, "lon": 0}, {"lat": 0, "lon": 0}]
    hole = [{"lat": .4, "lon": .4}, {"lat": .4, "lon": .6}, {"lat": .6, "lon": .6}, {"lat": .6, "lon": .4}, {"lat": .4, "lon": .4}]

    def fake_overpass(q):
        if "foreach" in q:
            return [{"tags": {"admin_level": "4", "name": "Bali"}},
                    {"id": 77, "tags": {"admin_level": "5", "name": "Kabupaten Badung"}}]
        if "out geom" in q:
            return [{"members": [{"type": "way", "role": "outer", "geometry": square},
                                 {"type": "way", "role": "inner", "geometry": hole}]}]
        return [{"type": "way", "id": 5, "tags": {"natural": "beach", "name": "Pantai Kuta", "surface": "sand"}},
                {"type": "way", "id": 6, "tags": {"natural": "beach", "name": "Mud Flat", "surface": "mud"}}]
    monkeypatch.setattr(s4_beach, "overpass", fake_overpass)
    monkeypatch.setattr(C, "SPOTCHECK_MIN_AGREE", 1)                     # fixture has 1 city, not 20
    C.DATA.mkdir(exist_ok=True)
    with zipfile.ZipFile(C.DATA / "geonames_ID.zip", "w") as z:
        z.writestr("ID.txt", "1\tPantai Kuta\tx\t\t0.2\t0.2\tT\tBCH\n2\tIn Hole\tx\t\t0.5\t0.5\tT\tBCH\n")
    s4_beach.main()
    city = read_rows("s4_cities.csv")[0]
    assert city["beach"] == "yes" and city["beach_names"] == "Pantai Kuta" and city["beach_source"].endswith("/way/5")
    spot = read_rows("s4_spotcheck.csv")[0]
    assert spot["geonames_names"] == "Pantai Kuta" and spot["agree"] == "yes"   # hole point excluded

    s5_deliver.main()
    wb = load_workbook(C.WORKBOOK)
    assert wb.sheetnames == ["Institutions", "Summary"]
    assert wb["Institutions"].max_row - 1 == len(rows)
    assert list(wb["Summary"].iter_rows(min_row=2, values_only=True)) == [("Kabupaten Badung", "Bali", len(rows), "yes")]


def test_s4_gate_fails_on_unmatched_city(monkeypatch):
    write_rows("s3_institutions.csv", [{"name": "A", "city": "Kota Nowhere", "province": "Bali"}], ["name", "city", "province"])
    (C.DATA / "osm_admin.json").write_text(json.dumps([]))
    with pytest.raises(SystemExit, match="Stage 4 gate FAILED"):
        s4_beach.main()


def test_s5_gate_fails_on_missing_beach(monkeypatch):
    write_rows("s3_institutions.csv", [{"name": "A", "city": "Kota Y", "province": "Bali", "duplicate": "no"}],
               ["name", "city", "province", "duplicate"])
    write_rows("s4_cities.csv", [], ["city", "province", "beach"])
    with pytest.raises(SystemExit, match="Stage 5 gate FAILED"):
        s5_deliver.main()
    assert not C.WORKBOOK.exists()
