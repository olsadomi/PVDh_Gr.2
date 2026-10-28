"""Step 7 - Feature engineering.

Age: end of "active life" = closure date -> passivation date (passive businesses) -> reference date (active ones).
A closed business with no closure date -> age unknown (NaN), not "until today".
"""
import numpy as np
import pandas as pd

from common.columns import C
from common.config import REFERENCE_DATE
from common.utils import show, step
from common.values import GENDER_STRUCTURE, FormGroup, LegalType, Status


def create_features(df):
    step("7. FEATURE ENGINEERING")
    # Temporal (day is not given -> first day of the month)
    df["registration_date"] = pd.to_datetime(dict(year=df[C.YEAR].astype(int),
                                                  month=df["registration_month"].astype(int), day=1))
    df["registration_quarter"] = df["registration_date"].dt.quarter

    # Binary status, age, lifespan
    df["is_active"] = (df["status"] == Status.REGISTERED).astype(int)
    df["is_closed"] = (df["status"] == Status.CLOSED).astype(int)
    end = df[C.CLOSURE_DATE].fillna(df["passivation_date"]).fillna(REFERENCE_DATE)
    df["age_years"] = ((end - df["registration_date"]).dt.days / 365.25).round(2).clip(lower=0)
    df.loc[(df["status"] == Status.CLOSED) & df[C.CLOSURE_DATE].isna(), "age_years"] = np.nan
    df["lifespan_closed_years"] = np.where(df["is_closed"].eq(1) & df[C.CLOSURE_DATE].notna(), df["age_years"], np.nan)
    df["left_censored_age"] = (df[C.YEAR] == 2000).astype(int)  # the register starts in 2000

    # Owners and gender
    df["owners_total"] = df[C.OWNERS_M] + df[C.OWNERS_F]
    df["has_female_owner"] = (df[C.OWNERS_F] > 0).astype(int)
    df["female_owner_share"] = np.where(df["owners_total"] > 0, df[C.OWNERS_F] / df["owners_total"], np.nan)
    df["gender_structure"] = np.select(
        [df["owners_total"] == 0, df[C.OWNERS_F] == 0, df[C.OWNERS_M] == 0],
        [GENDER_STRUCTURE["none"], GENDER_STRUCTURE["male"], GENDER_STRUCTURE["female"]], default=GENDER_STRUCTURE["mixed"])

    # Trade name, NACE hierarchy, grouped legal form (11 -> 4; 7 types have < 1% each)
    df["has_trade_name"] = df[C.TRADE_NAME].notna().astype(int)
    df["nace_division"] = df["nace_code"].str[:2]
    df["legal_form_group"] = np.select(
        [df[C.LEGAL_TYPE] == LegalType.SOLE,
         df[C.LEGAL_TYPE].isin([LegalType.LLC, LegalType.JSC]),
         df[C.LEGAL_TYPE].isin([LegalType.GENERAL_PARTNERSHIP, LegalType.LIMITED_PARTNERSHIP])],
        [FormGroup.INDIVIDUAL, FormGroup.COMPANY, FormGroup.PARTNERSHIP], default=FormGroup.OTHER)

    # Density at municipality level
    n_mun = df.groupby(C.MUNICIPALITY)[C.ID].transform("count")
    df["businesses_per_1000_municipality"] = (n_mun / df["population_2024"] * 1000).round(2)

    show(df[["age_years", "lifespan_closed_years", "owners_total", "female_owner_share"]].describe().round(2))
    show(df["legal_form_group"].value_counts())
    return df
