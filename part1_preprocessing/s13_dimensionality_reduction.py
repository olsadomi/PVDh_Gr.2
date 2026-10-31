"""Step 13 - Dimensionality reduction and feature subset selection.

13.1 Feature selection: (a) domain-based removal, (b) variance filter, (c) mutual information with `is_active`.
     `age_years` is excluded from MI: for closed businesses it is measured up to closure -> information leakage.
13.2 PCA on the municipality x section matrix (38 x 21, as shares within each municipality -> structure, not size).
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold, mutual_info_classif
from sklearn.preprocessing import StandardScaler

from common.columns import C
from common.config import OUT_PART1, PROCESSED, RANDOM_STATE, UNKNOWN
from common.utils import save_csv, save_figure, show, step

# Columns not used as model features (they stay in the exported dataset)
DOMAIN_REMOVAL = pd.DataFrame([
    (C.ID, "Identifier, carries no information"),
    (C.NAME, "Free text, high cardinality"),
    (C.TRADE_NAME, "Free text, 34% missing; represented by has_trade_name"),
    (C.STATUS, "Represented by status + passivation_date"),
    (C.NACE, "Represented by nace_code (+ nace_division)"),
    (C.SECTOR, "Represented by section_code"),
    (C.MONTH, "Represented by registration_month / registration_date"),
    ("employees_minmax / employees_zscore", "Demonstration only; log_employees is sufficient"),
], columns=["column", "reason"])


def select_features(df, strat):
    step("13.1 FEATURE SUBSET SELECTION")
    print("(a) Domain-based removal:"); show(DOMAIN_REMOVAL)

    cand = pd.concat([
        df[["log_employees", "age_years", "owners_total", C.OWNERS_M, C.OWNERS_F, "has_female_owner",
            "has_trade_name", "re_registered", "flag_nace_missing", "flag_employees_imputed", "registration_month",
            "registration_quarter"]].astype(float),
        pd.get_dummies(df["legal_form_group"], prefix="form", dtype=float)], axis=1)
    vt = VarianceThreshold(threshold=0.01).fit(cand)
    var = pd.DataFrame({"variance": cand.var().round(4), "kept (var > 0.01)": vt.get_support()})
    print("(b) Variance filter:"); show(var.sort_values("variance"))

    X = cand.loc[strat.index].drop(columns=["age_years"])
    y = df.loc[strat.index, "is_active"]
    mi = pd.Series(mutual_info_classif(X, y, discrete_features=[X[c].nunique() <= 13 for c in X.columns],
                                       random_state=RANDOM_STATE), index=X.columns, name="MI").sort_values(ascending=False)
    print("(c) Mutual information with is_active:"); show(mi.round(4))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    mi.plot.barh(ax=ax, color="#6250d6"); ax.invert_yaxis()
    ax.set_title("Mutual information with 'is_active'"); ax.set_xlabel("MI (nats)"); fig.tight_layout()
    save_figure(fig, OUT_PART1 / "fig04_mutual_information.png")
    return mi


def pca_municipalities(agg_municipality_sector):
    step("13.2 DIMENSIONALITY REDUCTION - PCA")
    M = agg_municipality_sector.set_index(C.MUNICIPALITY).drop(index=UNKNOWN, errors="ignore").drop(columns="X", errors="ignore")
    share = M.div(M.sum(axis=1), axis=0)
    Xs = StandardScaler().fit_transform(share)
    pca = PCA(random_state=RANDOM_STATE).fit(Xs)
    cum = np.cumsum(pca.explained_variance_ratio_)
    k80 = int(np.argmax(cum >= 0.80) + 1)
    print(f"Dimensions: {Xs.shape[1]} -> components for >= 80% of variance: {k80}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(range(1, len(cum) + 1), pca.explained_variance_ratio_ * 100, color="#2a78d6", label="individual")
    axes[0].plot(range(1, len(cum) + 1), cum * 100, "o-", color="#eb6834", label="cumulative")
    axes[0].axhline(80, ls="--", c="grey"); axes[0].legend(); axes[0].set_title("Scree plot - PCA (municipality x section)")
    Z = pca.transform(Xs)[:, :2]
    axes[1].scatter(Z[:, 0], Z[:, 1], c="#1baf7a", s=40)
    for i, n in enumerate(share.index):
        axes[1].annotate(n, (Z[i, 0], Z[i, 1]), fontsize=7)
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}%)")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}%)")
    axes[1].set_title("Municipalities in 2D PCA space"); fig.tight_layout()
    save_figure(fig, OUT_PART1 / "fig05_pca_municipalities.png")

    load = pd.DataFrame(pca.components_[:2].T, index=share.columns, columns=["PC1", "PC2"]).round(3)
    print("Largest loadings on PC1:"); show(load.reindex(load["PC1"].abs().sort_values(ascending=False).index).head(6))

    out = pd.DataFrame(pca.transform(Xs)[:, :k80], index=share.index, columns=[f"PC{i + 1}" for i in range(k80)]).reset_index()
    save_csv(out, PROCESSED / "pca_municipalities.csv")
    return out
