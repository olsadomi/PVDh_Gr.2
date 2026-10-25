"""Helpers: printing tables to the terminal, step headers, saving figures and CSV files."""
import warnings

import matplotlib

matplotlib.use("Agg")  # no window: figures are saved as PNG
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 60)
pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 60)
sns.set_theme(style="whitegrid")


def step(title: str) -> None:
    """Print the header of a pipeline step."""
    print("\n" + "=" * 90 + f"\n  {title}\n" + "=" * 90)


def show(obj, n: int | None = 30) -> None:
    """Print a DataFrame/Series to the terminal (the script equivalent of display() in a notebook)."""
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        print(obj.head(n).to_string() if n and len(obj) > n else obj.to_string())
    else:
        print(obj)


def save_figure(fig, path) -> None:
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [figure] {path.name}")


def save_csv(df, path, index: bool = False) -> None:
    df.to_csv(path, index=index, encoding="utf-8-sig")
    print(f"  [csv] {path.name}  ({len(df):,} rows)")
