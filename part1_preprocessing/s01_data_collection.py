"""Step 1 - Data collection.

Source:       ARBK (Kosovo Business Registration Agency) Open Data, snapshot 05.10.2026 (Excel, sheet 'Bizneset').
Integration:  ASK (Kosovo Agency of Statistics), "Population of Kosovo 2024", municipal estimates (31.12.2024), Table 3.

All columns are read as TEXT (dtype=str) so pandas does not guess types (leading zeros in IDs and date
formats are preserved). Types are defined explicitly in step 2.
"""

import pandas as pd

from common.config import POPULATION_CSV, RAW_CSV, RAW_XLSX
from common.utils import show, step


def read_raw_data() -> pd.DataFrame:
    step("1. DATA COLLECTION")
    if not RAW_XLSX.exists():
        raise FileNotFoundError(f"Place the ARBK Excel file at: {RAW_XLSX}")
    raw = pd.read_excel(RAW_XLSX, sheet_name="Bizneset", dtype=str)
    print(f"Rows: {raw.shape[0]:,} | Columns: {raw.shape[1]}")
    print("Source columns (names kept unchanged):", list(raw.columns))
    raw.to_csv(RAW_CSV, index=False, encoding="utf-8-sig")  # CSV copy (course requirement)
    print(f"CSV copy: {RAW_CSV.name}")
    show(raw.head(5))
    return raw


def read_population() -> pd.DataFrame:
    pop = pd.read_csv(POPULATION_CSV)
    assert len(pop) == 38, "Expected 38 municipalities"
    print(f"ASK population 2024: {len(pop)} municipalities, {pop['population_2024'].sum():,} residents in total")
    return pop