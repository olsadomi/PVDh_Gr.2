import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common.columns import C
from common.config import OUT_PART1, REFERENCE_DATE, SIZE_CLASSES
from common.utils import save_csv, save_figure, show, step
from common.values import Status

def completeness(df):
    c = pd.DataFrame({"missing": df[C.SOURCE].isna().sum(), "missing_%": (df[C.SOURCE].isna().mean() * 100).round(2)})
    c = c.sort_values("missing", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    cc = c[c["missing"] > 0]
    ax.barh(cc.index, cc["missing_%"], color="#2a78d6")
    for i, v in enumerate(cc["missing_%"]):
        ax.text(v + 0.5, i, f"{v:.2f}%", va="center", fontsize=9)
    ax.set_xlabel("% missing values"); ax.set_title("Column completeness (before cleaning)")
    ax.invert_yaxis(); fig.tight_layout()
    save_figure(fig, OUT_PART1 / "fig01_completeness.png")
    return c

def uniqueness(df):
    dup = df[df[C.ID].notna() & df.duplicated(C.ID, keep=False)]
    print("Fully identical rows:", df.duplicated().sum())
    print(f"Rows with a repeated ID: {len(dup)} -> {dup[C.ID].nunique()} IDs")
    print("Status pairs within duplicates:",
          dup.groupby(C.ID)[C.STATUS].apply(lambda s: " + ".join(sorted(s))).value_counts().to_dict())
    return dup

def validity(df, standard_municipalities):
    id_len = df[C.ID].str.len()
    non_std = df.loc[df[C.MUNICIPALITY].notna() & ~df[C.MUNICIPALITY].isin(standard_municipalities), C.MUNICIPALITY].value_counts()
    v = pd.Series({
        f"{C.ID} missing": df[C.ID].isna().sum(),
        f"{C.ID} not digits only": (~df[C.ID].fillna("0").str.fullmatch(r"\d+")).sum(),
        f"{C.ID} with 8 digits (legacy format)": (id_len == 8).sum(),
        f"{C.EMPLOYEES} < 0": (df[C.EMPLOYEES] < 0).sum(),
        f"{C.EMPLOYEES} == 0": (df[C.EMPLOYEES] == 0).sum(),
        f"{C.YEAR} outside [2000, 2026]": (~df[C.YEAR].between(2000, 2026)).sum(),
        f"{C.CLOSURE_DATE} after snapshot": (df[C.CLOSURE_DATE] > REFERENCE_DATE).sum(),
        f"{C.MUNICIPALITY} non-standard": int(non_std.sum()),
    }, name="count")
    show(v)
    print("  Non-standard municipalities:", non_std[non_std > 0].to_dict())
    return v


def consistency(df):
    status = df[C.STATUS].str.split("-").str[0]
    emp = df[C.EMPLOYEES]
    size_from_emp = pd.cut(emp.astype(float), [-np.inf, 9, 49, 249, np.inf], labels=SIZE_CLASSES)
    division = df[C.NACE].astype(str).str.extract(r"^(\d{2})")[0]
    c = pd.Series({
        '"Shuar" without a closure date': ((status == Status.CLOSED) & df[C.CLOSURE_DATE].isna()).sum(),
        '"Regjistruar" with a closure date': ((status == Status.REGISTERED) & df[C.CLOSURE_DATE].notna()).sum(),
        '"Pasiv" with a closure date': ((status == Status.PASSIVE) & df[C.CLOSURE_DATE].notna()).sum(),
        "Closure date before registration year": (df[C.CLOSURE_DATE].dt.year < df[C.YEAR]).sum(),
        "Size class != employee class": ((df[C.SIZE].astype(str) != size_from_emp.astype(str))
                                         & df[C.SIZE].notna() & emp.notna()).sum(),
        "Size class missing, employees present": (df[C.SIZE].isna() & emp.notna()).sum(),
        "NACE division mapped to > 1 sector": int((df.groupby(division)[C.SECTOR].nunique() > 1).sum()),
    }, name="count")
    show(c)
    return c