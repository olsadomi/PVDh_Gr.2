"""Step 12 - Sampling.

Some Part II methods (LOF, statistical tests) are slow or give "always significant" p-values with 272k rows.
Two 10% samples are compared: simple random (SRS) and stratified (legal_form_group x status).
The stratified sample preserves the proportions better (even for small strata) and is saved for Part II.
"""
import pandas as pd

from common.config import RANDOM_STATE, SAMPLE_CSV
from common.utils import save_csv, show, step


def sample(df, frac: float = 0.10) -> pd.DataFrame:
    step("12. SAMPLING")
    strata = df["legal_form_group"] + " | " + df["status"]
    srs = df.sample(frac=frac, random_state=RANDOM_STATE)
    strat = df.groupby(strata, group_keys=False).sample(frac=frac, random_state=RANDOM_STATE)

    pop_p = strata.value_counts(normalize=True)
    c = pd.DataFrame({
        "population_%": pop_p * 100,
        "SRS_%": strata.loc[srs.index].value_counts(normalize=True).reindex(pop_p.index) * 100,
        "stratified_%": strata.loc[strat.index].value_counts(normalize=True).reindex(pop_p.index) * 100,
    }).fillna(0)
    c["error_SRS"] = (c["SRS_%"] - c["population_%"]).abs()
    c["error_stratified"] = (c["stratified_%"] - c["population_%"]).abs()
    show(c.round(3))
    print(f"Mean absolute error -> SRS: {c['error_SRS'].mean():.4f} pp | Stratified: {c['error_stratified'].mean():.4f} pp")
    save_csv(strat, SAMPLE_CSV)
    return strat
