"""Step 6 - Integration.

(1) ARBK + ASK (population by municipality, 2024) + municipality -> region mapping (7 regions):
    enables normalised metrics (businesses per 1,000 residents).
    WARNING: population is an ASK ESTIMATE (31.12.2024). The region mapping should be verified.
(2) Internal integration: a NACE dimension table (for the Power BI star schema).
"""
from common.columns import C
from common.config import UNKNOWN
from common.utils import show, step


def integrate(df, pop):
    step("6. INTEGRATION")
    before = len(df)
    df = df.merge(pop, left_on=C.MUNICIPALITY, right_on="municipality", how="left",
                  validate="many_to_one", indicator=True)
    assert len(df) == before, "Integration must not change the number of rows"
    show(df["_merge"].value_counts())
    print("Municipalities without a match:", list(df.loc[df["_merge"] == "left_only", C.MUNICIPALITY].unique()))
    print("ASK municipalities without any business:", set(pop["municipality"]) - set(df[C.MUNICIPALITY]))
    df = df.drop(columns=["_merge", "municipality"])
    df["region"] = df["region"].fillna(UNKNOWN)

    dim_nace = (df[["nace_code", "nace_description", "section_code", "section_name"]]
                .drop_duplicates("nace_code").sort_values("nace_code").reset_index(drop=True))
    dim_nace["nace_division"] = dim_nace["nace_code"].str[:2]
    assert dim_nace["nace_code"].is_unique
    print(f"dim_nace: {len(dim_nace)} codes, {dim_nace['section_code'].nunique()} sections")
    return df, dim_nace
