# bfa_core/growth_metrics.py

import pandas as pd


def add_growth_and_rule_of_40(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add growth metrics and Rule of 40.
    If there's only one period, leaves them as None.
    """
    df = df.copy()

    if len(df) < 2:
        df["RevenueGrowth"] = None
        df["NetIncomeGrowth"] = None
        df["RuleOf40"] = None
        return df

    df = df.sort_values("Year").reset_index(drop=True)

    if "Revenue" in df.columns:
        df["RevenueGrowth"] = df["Revenue"].pct_change()
    else:
        df["RevenueGrowth"] = None

    if "NetIncome" in df.columns:
        df["NetIncomeGrowth"] = df["NetIncome"].pct_change()
    else:
        df["NetIncomeGrowth"] = None

    df["RuleOf40"] = None
    last_idx = df.index[-1]
    growth = df.loc[last_idx, "RevenueGrowth"]
    margin = df.loc[last_idx, "NetMargin"] if "NetMargin" in df.columns else None

    if pd.notnull(growth) and pd.notnull(margin):
        df.loc[last_idx, "RuleOf40"] = 100 * (growth + margin)

    return df
