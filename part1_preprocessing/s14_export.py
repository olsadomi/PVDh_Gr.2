"""Step 14 - Export (the contract with Part II).

`arbk_clean.csv`: 1 row = 1 unique business. All 15 source columns keep their original names (cleaned values),
followed by the derived columns (English names). No missing values in the analytical columns; data-quality flags kept.
Extreme values have NOT been touched: they are printed as an open question for Part II.
"""
import pandas as pd

from common.columns import C
from common.config import CLEAN_CSV, OUT_PART1, PROCESSED
from common.utils import save_csv, show, step

DERIVED_COLUMNS = [
    "re_registered", "legal_form_group", "status", "is_active", "is_closed", "passivation_date",
    "nace_code", "nace_description", "nace_division", "section_code", "section_name",
    "region", "population_2024", "businesses_per_1000_municipality",
    "log_employees", "owners_total", "has_female_owner", "female_owner_share", "gender_structure", "has_trade_name",
    "registration_month", "registration_quarter", "registration_date", "registration_period",
    "age_years", "age_group", "lifespan_closed_years", "left_censored_age",
    "flag_nace_missing", "flag_employees_imputed", "flag_invalid_closure_date", "flag_status_date_conflict",
]


def export(df, dim_nace):
    step("14. EXPORT - INPUT FOR PART II")
    clean = df[C.SOURCE + DERIVED_COLUMNS].copy()
    save_csv(clean, CLEAN_CSV)
    save_csv(dim_nace, PROCESSED / "dim_nace.csv")
    dictionary = pd.DataFrame({"column": clean.columns,
                               "origin": ["source"] * len(C.SOURCE) + ["derived"] * len(DERIVED_COLUMNS),
                               "dtype": clean.dtypes.astype(str).values,
                               "missing": clean.isna().sum().values, "unique": clean.nunique().values})
    save_csv(dictionary, OUT_PART1 / "05_data_dictionary.csv")
    print(f"\narbk_clean.csv -> {clean.shape[0]:,} rows x {clean.shape[1]} columns")
    print("\nOpen question for Part II - the most extreme values (untouched here):")
    show(clean.nlargest(8, C.EMPLOYEES)[[C.NAME, C.LEGAL_TYPE, C.EMPLOYEES, "owners_total"]])
    return clean
