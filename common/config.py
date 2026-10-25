"""Project paths and constants, defined in one place."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Input data
RAW_XLSX = ROOT / "data" / "raw" / "Bizneset_2026-10-05.xlsx"
RAW_CSV = ROOT / "data" / "raw" / "businesses_2026-10-05_raw.csv"
EXTERNAL = ROOT / "data" / "external"
POPULATION_CSV = EXTERNAL / "population_municipalities_2024.csv"
GEOJSON = EXTERNAL / "geo" / "geoBoundaries-XKX-ADM2_simplified.geojson"
PROCESSED = ROOT / "data" / "processed"

# Outputs per part
OUT_PART1 = ROOT / "outputs" / "part1"
OUT_PART2 = ROOT / "outputs" / "part2"
OUT_PART3 = ROOT / "outputs" / "part3"
POWERBI = ROOT / "powerbi"

# Files that connect the parts (the contract between phases)
CLEAN_CSV = PROCESSED / "arbk_clean.csv"          # Part I  -> Part II
ANALYSIS_CSV = PROCESSED / "arbk_analysis.csv"    # Part II -> Part III
SAMPLE_CSV = PROCESSED / "arbk_stratified_sample_10pct.csv"

# Constants
REFERENCE_DATE = pd.Timestamp("2026-10-05")       # date of the ARBK snapshot
RANDOM_STATE = 42
SIZE_CLASSES = ["0-9", "10-49", "50-249", "250-"]  # labels as in the source column "Madhësia"
KOSOVO_POPULATION_2024 = 1_585_590
NORTHERN_MUNICIPALITIES = ["Zveçan", "Mitrovicë Veriore", "Leposaviq", "Zubin Potok"]
from common.values import UNKNOWN  # noqa: E402,F401  ("E panjohur")

for d in (PROCESSED, OUT_PART1, OUT_PART2, OUT_PART3, POWERBI):
    d.mkdir(parents=True, exist_ok=True)
