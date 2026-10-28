"""Step 5 - Identifying missing values and choosing a handling strategy.

Before choosing a strategy: WHY is the value missing? (MCAR / MAR / MNAR)
Key finding: NACE is missing mainly for registrations before 2008 -> MAR (depends on year, which is observed).
Imputing the mode ("G - Trade") would distort the sector structure of the 2000s.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from common.columns import C
from common.config import OUT_PART1, SIZE_CLASSES, UNKNOWN
from common.utils import save_csv, save_figure, show, step

STRATEGY = pd.DataFrame([
    (C.TRADE_NAME, "34.4%", "Structural (optional field)", "Not imputed", "Binary feature has_trade_name is created"),
    (f"{C.NACE} / {C.SECTOR}", "3.6%", "MAR (depends on year)", "'E panjohur' category in nace_code/section_* + flag",
     "Mode imputation would distort the 2000s sector structure"),
    (C.EMPLOYEES, "0.6%", "MCAR/MAR (few)", f"Median by '{C.LEGAL_TYPE}' + flag",
     "Highly skewed; mean (2.3) is biased; group median keeps sole proprietorship vs JSC differences"),
    (C.SIZE, "0.7%", "Derived", f"Recomputed from '{C.EMPLOYEES}'", "Deterministic function (EU: 0-9, 10-49, 50-249, 250+)"),
    (C.MUNICIPALITY, "0.01%", "MCAR (40 rows)", "'E panjohur' category", "Kept for national totals"),
    (C.CLOSURE_DATE, "86.9%", "Structural (active businesses have none)", "Not imputed", "Used as censoring in survival analysis"),
], columns=["column", "missing", "mechanism", "strategy", "rationale"])


def analyse_mechanism(df):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    by_year = df.groupby(C.YEAR)["nace_code"].apply(lambda s: s.isna().mean() * 100)
    axes[0].bar(by_year.index.astype(int), by_year.values, color="#e34948")
    axes[0].set_title("% NACE missing, by registration year"); axes[0].set_xlabel("Year"); axes[0].set_ylabel("%")
    by_type = df.groupby(C.LEGAL_TYPE, observed=True)["nace_code"].apply(lambda s: s.isna().mean() * 100).sort_values()
    axes[1].barh(by_type.index.astype(str), by_type.values, color="#e34948"); axes[1].set_title("% NACE missing, by legal type")
    fig.tight_layout(); save_figure(fig, OUT_PART1 / "fig02_nace_missingness_mechanism.png")

    ct = pd.crosstab(df["nace_code"].isna(), df[C.YEAR] < 2008)
    chi2, p, _, _ = chi2_contingency(ct)
    print(f"Chi-square: NACE missing vs (registered before 2008) -> chi2={chi2:,.0f}, p={p:.2e} => not MCAR (MAR on year)")


def handle(df):
    step("5. MISSING VALUES - MECHANISM AND STRATEGY")
    analyse_mechanism(df)
    show(STRATEGY)
    save_csv(STRATEGY, OUT_PART1 / "03_missing_value_strategy.csv")

    # a) NACE -> "E panjohur" + flag (in the derived columns; the source columns stay as published)
    df["flag_nace_missing"] = df["nace_code"].isna().astype(int)
    df["nace_code"] = df["nace_code"].fillna("0000")
    df["nace_description"] = df["nace_description"].fillna(UNKNOWN)
    df["section_code"] = df["section_code"].fillna("X")
    df["section_name"] = df["section_name"].fillna(UNKNOWN)

    # b) Employees -> median by legal type + flag
    df["flag_employees_imputed"] = df[C.EMPLOYEES].isna().astype(int)
    med = df.groupby(C.LEGAL_TYPE, observed=True)[C.EMPLOYEES].median()
    print("Median employees by legal type:"); show(med)
    df[C.EMPLOYEES] = df[C.EMPLOYEES].fillna(df[C.LEGAL_TYPE].map(med).astype(float).round()).astype("Int64")

    # c) Size class -> recomputed (also fixes the mismatches and the 0-employee cases)
    size = pd.cut(df[C.EMPLOYEES].astype(float), [-np.inf, 9, 49, 249, np.inf], labels=SIZE_CLASSES)
    print("Size class changed/filled:", (size.astype(str) != df[C.SIZE].astype(str)).sum())
    df[C.SIZE] = size

    # d) Municipality -> "E panjohur"
    df[C.MUNICIPALITY] = df[C.MUNICIPALITY].fillna(UNKNOWN)

    print("Missing after handling:")
    show(df[["nace_code", "section_code", C.EMPLOYEES, C.SIZE, C.MUNICIPALITY, "status"]].isna().sum())
    return df
