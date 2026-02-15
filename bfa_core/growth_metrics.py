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
        df["SaaSMagicNumber"] = None
        return df

    # Sort by Year (and Period as tiebreaker if needed)
    sort_cols = ["Year"] if "Year" in df.columns else []
    if "Period" in df.columns:
        sort_cols.append("Period")
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    # Revenue growth
    if "Revenue" in df.columns:
        df["RevenueGrowth"] = df["Revenue"].pct_change()
    else:
        df["RevenueGrowth"] = None

    # Net income growth
    if "NetIncome" in df.columns:
        df["NetIncomeGrowth"] = df["NetIncome"].pct_change()
    else:
        df["NetIncomeGrowth"] = None

    # Rule of 40: growth + net margin for last period
    df["RuleOf40"] = None
    last_idx = df.index[-1]
    growth = df.loc[last_idx, "RevenueGrowth"]
    margin = df.loc[last_idx, "NetMargin"] if "NetMargin" in df.columns else None

    if pd.notnull(growth) and pd.notnull(margin):
        df.loc[last_idx, "RuleOf40"] = 100 * (growth + margin)

    # SaaS Magic Number (quarterly assumption)
    # MagicNumber_t = (Revenue_t - Revenue_{t-1}) * 4 / Marketing_{t-1}
    df["SaaSMagicNumber"] = None
    if "Revenue" in df.columns and "Marketing" in df.columns:
        for i in range(1, len(df)):
            rev_t = df.loc[i, "Revenue"]
            rev_prev = df.loc[i - 1, "Revenue"]
            m_prev = df.loc[i - 1, "Marketing"]

            if pd.notnull(rev_t) and pd.notnull(rev_prev) and m_prev not in (0, None) and not pd.isna(m_prev):
                df.loc[i, "SaaSMagicNumber"] = ((rev_t - rev_prev) * 4.0) / m_prev

    return df
