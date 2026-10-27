"""Step 4 - Cleaning.

Every intervention is logged (rows affected, action taken) so the process is reproducible.
Source columns keep their names; composite source columns are split into NEW columns (the source stays).
The official status is kept even when it conflicts with the date (4.7): changing it would invent a fact;
with a flag, Part II can exclude these rows from lifespan analysis.
"""
import numpy as np
import pandas as pd

from common.columns import C
from common.config import OUT_PART1
from common.values import Status
from common.utils import save_csv, show, step


class CleaningLog:
    def __init__(self):
        self.rows = []

    def __call__(self, step_name, n, action):
        self.rows.append({"step": step_name, "rows_affected": int(n), "action": action})

    def df(self):
        return pd.DataFrame(self.rows)



