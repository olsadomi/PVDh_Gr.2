"""Step 4 - Cleaning.

Every intervention is logged (rows affected, action taken) so the process is reproducible.
Source columns keep their names; composite source columns are split into NEW columns (the source stays).
The official status is kept even when it conflicts with the date (4.7): changing it would invent a fact;
with a flag, Part II can exclude these rows from lifespan analysis.
"""
import numpy as np
import pandas as pd

from common.columns import C
from common.config import OUT_PART1
from common.values import Status
from common.utils import save_csv, show, step


class CleaningLog:
    def __init__(self):
        self.rows = []

    def __call__(self, step_name, n, action):
        self.rows.append({"step": step_name, "rows_affected": int(n), "action": action})

    def df(self):
        return pd.DataFrame(self.rows)


def clean(df: pd.DataFrame):
    step("4. CLEANING")
    log = CleaningLog()
    n0 = len(df)

    # 4.1 Row without an ID: cannot be identified or joined
    m = df[C.ID].isna()
    df = df[~m].copy(); log("4.1 Missing ID", m.sum(), "Row removed")

    # 4.2 Duplicated ID (re-registration): keep the most recent registration
    df = df.sort_values([C.ID, C.YEAR, "registration_month"])
    df["re_registered"] = df.duplicated(C.ID, keep=False).astype(int)
    m = df.duplicated(C.ID, keep="last")
    df = df[~m].copy(); log("4.2 Duplicated ID", m.sum(), "Kept most recent registration, flag re_registered=1")

    # 4.3 Standardise municipality spelling
    m = df[C.MUNICIPALITY].astype(str) == "Zvecane"
    df[C.MUNICIPALITY] = df[C.MUNICIPALITY].astype(str).replace({"Zvecane": "Zveçan", "nan": np.nan})
    log("4.3 Municipality", m.sum(), "'Zvecane' -> 'Zveçan'")

    # 4.4 'Pasiv-09/06/2022' -> new columns: status ('Pasiv') + passivation_date (2022-06-09)
    parts = df[C.STATUS].str.split("-", n=1, expand=True)
    df["status"] = parts[0]
    assert df["status"].isin(Status.ALL).all(), f"Unexpected status values: {set(df['status']) - set(Status.ALL)}"
    df["passivation_date"] = pd.to_datetime(parts[1], format="%d/%m/%Y", errors="coerce")
    log("4.4 Status", df["passivation_date"].notna().sum(), "Embedded date split off into status + passivation_date")

    # 4.5 Negative employees -> NaN (handled in step 5)
    m = (df[C.EMPLOYEES] < 0).fillna(False).astype(bool)
    df.loc[m, C.EMPLOYEES] = pd.NA; log("4.5 Employees < 0", m.sum(), "Negative value -> NaN")

    # 4.6 Closure date before registration -> invalid
    m = (df[C.CLOSURE_DATE].dt.year < df[C.YEAR]).fillna(False).astype(bool)
    df["flag_invalid_closure_date"] = m.astype(int)
    df.loc[m, C.CLOSURE_DATE] = pd.NaT
    log("4.6 Closure < registration", m.sum(), "Date -> NaT + flag")

    # 4.7 Status/date conflict: flag only
    df["flag_status_date_conflict"] = (
        ((df["status"] == Status.CLOSED) & df[C.CLOSURE_DATE].isna())
        | (df["status"].isin([Status.REGISTERED, Status.PASSIVE]) & df[C.CLOSURE_DATE].notna())).astype(int)
    log("4.7 Status/date conflict", df["flag_status_date_conflict"].sum(), "Flag only; official status kept")

    # 4.8 Atomic columns: NACE code / description; section code / name (texts as published in the file)
    nace = df[C.NACE].astype(str).str.extract(r"^(?P<code>\d{4})-(?P<desc>.+)$")
    df["nace_code"], df["nace_description"] = nace["code"], nace["desc"]
    sec = df[C.SECTOR].astype(str).str.extract(r"^(?P<code>[A-U]) - (?P<name>.+)$")
    df["section_code"], df["section_name"] = sec["code"], sec["name"]
    log("4.8 NACE", df["nace_code"].notna().sum(), "Code and description split into new columns")

    show(log.df())
    print(f"Rows: {n0:,} -> {len(df):,} (removed {n0 - len(df)})")
    save_csv(log.df(), OUT_PART1 / "04_cleaning_log.csv")
    return df, log
