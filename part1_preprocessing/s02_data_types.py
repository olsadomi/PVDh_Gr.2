"""Step 2 - Defining the data types.

First the CONCEPTUAL type (measurement scale) is defined, then the TECHNICAL pandas type.
The conceptual type determines which statistics and which charts are valid for a column.
Source column names are kept exactly as in the ARBK file.

Note on `Total M` / `Total F`: the column name does not say whether these are employees or owners.
In 39% of rows M+F != `Nr. punëtorëve`; for sole proprietorships M+F is always 0 or 1; public enterprises with
thousands of employees have M = F = 0. They are therefore interpreted as the NUMBER OF OWNERS by gender
(to be confirmed with ARBK documentation).
"""
import numpy as np
import pandas as pd

from common.columns import C
from common.config import OUT_PART1, SIZE_CLASSES
from common.values import LegalType, MONTHS
from common.utils import save_csv, show, step


def data_type_table() -> pd.DataFrame:
    return pd.DataFrame([
        (C.ID, "Identifier", "Nominal (ID)", "string", "Unique key; not a measurement"),
        (C.NAME, "Text", "Nominal (high cardinality)", "string", "Legal name"),
        (C.TRADE_NAME, "Text", "Nominal (high cardinality)", "string", "Trade name (optional)"),
        (C.LEGAL_TYPE, "Categorical", "Nominal", "category", "Legal form (11 values)"),
        (C.NACE, "Categorical (hierarchical)", "Nominal", "category", "NACE Rev.2 code + description"),
        (C.SECTOR, "Categorical (hierarchical)", "Nominal", "category", "NACE section (A-U)"),
        (C.EMPLOYEES, "Numeric discrete", "Ratio", "Int64", "Count; true zero"),
        (C.SIZE, "Categorical", "Ordinal", "ordered category", "0-9 < 10-49 < 50-249 < 250-"),
        (C.OWNERS_M, "Numeric discrete", "Ratio", "Int64", "Number of male owners (interpretation)"),
        (C.OWNERS_F, "Numeric discrete", "Ratio", "Int64", "Number of female owners (interpretation)"),
        (C.MUNICIPALITY, "Categorical / Geographic", "Nominal", "category", "Municipality (38)"),
        (C.STATUS, "Categorical", "Nominal", "category", "Contains an embedded date (Pasiv-09/06/2022)"),
        (C.YEAR, "Temporal", "Interval", "Int64", "Year of registration"),
        (C.MONTH, "Temporal", "Ordinal (cyclical)", "string -> Int64", "Month name; numeric copy in registration_month"),
        (C.CLOSURE_DATE, "Temporal", "Interval", "datetime64", "Format dd/mm/yyyy"),
    ], columns=["column", "conceptual_type", "measurement_scale", "pandas_type", "note"])


def convert_types(raw: pd.DataFrame) -> pd.DataFrame:
    step("2. DATA TYPES")
    types = data_type_table()
    show(types)
    save_csv(types, OUT_PART1 / "01_data_types.csv")

    df = raw.copy()
    assert list(df.columns) == C.SOURCE, "Unexpected source columns"

    # 2.1 Extra whitespace; empty string -> NaN
    for c in df.columns:
        df[c] = df[c].str.strip().str.replace(r"\s{2,}", " ", regex=True)
        df.loc[df[c] == "", c] = np.nan

    # 2.2 Numeric columns (errors="coerce": any non-numeric value -> NaN, counted below)
    for c in [C.EMPLOYEES, C.OWNERS_M, C.OWNERS_F, C.YEAR]:
        before = df[c].notna().sum()
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
        print(f"  {c:20s} non-numeric -> NaN: {before - df[c].notna().sum()}")

    # 2.3 Month name -> number (new column; the source column is kept as it is)
    df["registration_month"] = df[C.MONTH].map(MONTHS).astype("Int64")
    print("  Unknown months:", df["registration_month"].isna().sum())

    # 2.4 Closure date
    df[C.CLOSURE_DATE] = pd.to_datetime(df[C.CLOSURE_DATE], format="%d/%m/%Y", errors="coerce")
    print("  Closure date range:", df[C.CLOSURE_DATE].min().date(), "->", df[C.CLOSURE_DATE].max().date())

    # 2.5 Categories; size class is ordinal with an explicit order
    for c in [C.LEGAL_TYPE, C.SECTOR, C.MUNICIPALITY, C.NACE]:
        df[c] = df[c].astype("category")
    df[C.SIZE] = pd.Categorical(df[C.SIZE], categories=SIZE_CLASSES, ordered=True)

    # Every legal type must be one of the 11 known values (catches a changed or new category in a future file)
    unknown_types = set(df[C.LEGAL_TYPE].dropna()) - set(LegalType.ALL)
    assert not unknown_types, f"Unexpected values in '{C.LEGAL_TYPE}': {unknown_types}"
    show(df.dtypes)
    return df
