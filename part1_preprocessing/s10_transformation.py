"""Step 10 - Transformation.

Min-max and z-score are LINEAR: they change the scale, not the shape (skewness stays the same).
Only log(1+x) reduces skewness, so `log_employees` is used for outlier detection in Part II.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from common.columns import C
from common.config import OUT_PART1
from common.utils import save_figure, show, step


def transform(df):
    step("10. TRANSFORMATION")
    x = df[C.EMPLOYEES].astype(float)
    df["log_employees"] = np.log1p(x)
    df["employees_minmax"] = MinMaxScaler().fit_transform(x.to_frame()).ravel()
    df["employees_zscore"] = StandardScaler().fit_transform(x.to_frame()).ravel()
    df["age_zscore"] = StandardScaler().fit_transform(df[["age_years"]]).ravel()

    cols = {"original": x, "log(1+x)": df["log_employees"], "min-max": df["employees_minmax"], "z-score": df["employees_zscore"]}
    show(pd.DataFrame({k: [v.skew(), v.min(), v.max()] for k, v in cols.items()}, index=["skewness", "min", "max"]).round(3))

    fig, axes = plt.subplots(1, 3, figsize=(15, 3.8))
    for ax, (name, color) in zip(axes, [("original", "#2a78d6"), ("log(1+x)", "#1baf7a"), ("min-max", "#eb6834")]):
        ax.hist(cols[name], bins=60, color=color); ax.set_yscale("log"); ax.set_title(f"{name} (log y-axis)")
    fig.suptitle("Transformations of the number of employees", y=1.02); fig.tight_layout()
    save_figure(fig, OUT_PART1 / "fig03_transformations.png")
    return df
