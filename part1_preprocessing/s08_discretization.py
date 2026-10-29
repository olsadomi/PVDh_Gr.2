"""Step 8 - Discretization.

Three methods are compared for business age: equal width, equal frequency (quantiles), domain intervals.
Conclusion: quantiles give bin edges with no business meaning; equal width puts most rows into 1-2 bins;
domain intervals (business life cycle) are chosen. For employees, quantiles cannot even be computed
(50% of values = 1), so the EU size classification (`Madhësia`) is used.
"""
import numpy as np
import pandas as pd

from common.columns import C
from common.utils import show, step
from common.values import AGE_GROUPS


def discretize(df):
    step("8. DISCRETIZATION")
    age = df["age_years"]
    print("- Equal width:"); show(pd.cut(age, bins=5).value_counts(sort=False))
    print("- Quantiles:"); show(pd.qcut(age, q=5, duplicates="drop").value_counts(sort=False))
    domain = pd.cut(age, bins=[-0.01, 1, 3, 5, 10, 20, np.inf], labels=AGE_GROUPS)
    print("- Domain intervals (chosen):"); show(domain.value_counts(sort=False))
    df["age_group"] = domain

    try:
        pd.qcut(df[C.EMPLOYEES].astype(float), q=4)
    except ValueError as e:
        print("qcut on employees fails:", str(e).split(".")[0])
    print("Employee quantiles:", df[C.EMPLOYEES].astype(float).quantile([.25, .5, .75, .9, .99]).to_dict())

    return df
