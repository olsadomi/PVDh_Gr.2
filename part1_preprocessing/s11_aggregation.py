"""Step 11 - Aggregation.

Aggregation changes the UNIT OF ANALYSIS (business -> municipality / year / sector): it reduces noise and produces
the tables used directly in the visualisations (Part III).

WARNING: northern municipalities have very low estimated populations in ASK 2024 (possibly limited census
participation - to be verified), which inflates "per 1,000 residents" figures.
"""
import pandas as pd

from common.columns import C
from common.config import PROCESSED
from common.utils import save_csv, show, step


def aggregate(df) -> dict:
    step("11. AGGREGATION")
    m = df.groupby([C.MUNICIPALITY, "region"], observed=True).agg(
        businesses=(C.ID, "count"), active=("is_active", "sum"), closed=("is_closed", "sum"),
        employees_total=(C.EMPLOYEES, "sum"), with_female_owner=("has_female_owner", "sum"),
        mean_age=("age_years", "mean"), population_2024=("population_2024", "first")).reset_index()
    m["active_%"] = (m["active"] / m["businesses"] * 100).round(1)
    m["female_owner_%"] = (m["with_female_owner"] / m["businesses"] * 100).round(1)
    m["active_per_1000"] = (m["active"] / m["population_2024"] * 1000).round(1)
    m = m.sort_values("active_per_1000", ascending=False)
    print("- Municipalities (top 10 by active per 1,000 residents):"); show(m.head(10))

    reg = df.groupby(C.YEAR).size().rename("registrations")
    clo = df[C.CLOSURE_DATE].dropna().dt.year.astype(int).value_counts().sort_index().rename("closures")
    y = pd.concat([reg, clo], axis=1).fillna(0).astype(int)
    y.index = y.index.astype(int); y.index.name = "year"
    y["net"] = y["registrations"] - y["closures"]
    print("- Yearly series (last 8 years):"); show(y.tail(8))

    sp = pd.crosstab(df["section_code"] + " - " + df["section_name"].str[:35], df["registration_period"],
                     normalize="columns", rownames=["section"]).mul(100).round(1)
    print("- Sector x period (%):"); show(sp.sort_values(sp.columns[-1], ascending=False).head(10))

    ms = pd.crosstab(df[C.MUNICIPALITY], df["section_code"])
    print("Municipality x section matrix:", ms.shape)

    tables = {"agg_municipality": m, "agg_year": y.reset_index(), "agg_sector_period": sp.reset_index(),
              "agg_municipality_sector": ms.reset_index()}
    for name, t in tables.items():
        save_csv(t, PROCESSED / f"{name}.csv")
    return tables
