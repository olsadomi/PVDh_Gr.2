import pandas as pd

from common.utils import show, step


def binarize(df, k: int = 8) -> pd.DataFrame:
    step("9. BINARIZATION")
    onehot = pd.get_dummies(df[["legal_form_group", "status", "region"]], prefix=["form", "status", "region"], dtype=int)
    top = df["section_code"].value_counts().head(k).index
    sections = pd.get_dummies(df["section_code"].where(df["section_code"].isin(top), "Other"), prefix="sec", dtype=int)
    matrix = pd.concat([onehot, sections, df[["has_female_owner", "has_trade_name", "re_registered"]]], axis=1)
    print(f"Binary matrix: {matrix.shape} | density (share of 1s): {matrix.values.mean():.3f}")
    show(matrix.head(3))
    return matrix
