# bfa_core/numeric_processing.py

import pandas as pd


def standardize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B1 – Standardization & sanity checks
    """
    numeric_cols = [
        "Revenue", "COGS", "Salaries", "Marketing", "Rent", "OtherOpex",
        "CurrentAssets", "CurrentLiab", "TotalAssets", "TotalLiab", "Equity", "Cash"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[numeric_cols].isnull().all(axis=None):
        raise ValueError("No usable numeric data found in required fields.")

    # simple non-negative check for main flows
    for col in ["Revenue", "COGS", "Salaries", "Marketing", "Rent"]:
        if col in df.columns and (df[col] < 0).any():
            raise ValueError(f"Negative values found in {col}, not allowed for this prototype.")

    return df


def build_income_statement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B2 – Income statement reconstruction
    """
    result = df.copy()

    # Gross profit
    result["GrossProfit"] = result["Revenue"] - result["COGS"]

    # Operating expenses (prototype: Salaries + Marketing + Rent + OtherOpex)
    opx_cols = [c for c in ["Salaries", "Marketing", "Rent", "OtherOpex"] if c in result.columns]
    result["OperatingExpenses"] = result[opx_cols].sum(axis=1)

    # Operating income
    result["OperatingIncome"] = result["GrossProfit"] - result["OperatingExpenses"]

    # Simple tax assumption: 20% of positive OperatingIncome
    tax_rate = 0.20
    result["TaxExpense_est"] = result["OperatingIncome"].apply(
        lambda x: tax_rate * x if x > 0 else 0.0
    )

    # Net income
    result["NetIncome"] = result["OperatingIncome"] - result["TaxExpense_est"]

    return result


def compute_core_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B3 – Core prototype ratios (we can later expand to all 25).
    """
    result = df.copy()

    # Safe division helper
    def safe_div(num, den):
        return num / den if den not in (0, None) else None

    # Per-row ratios
    ratios = []
    for _, row in result.iterrows():
        r = {}

        revenue = row.get("Revenue", None)
        gross_profit = row.get("GrossProfit", None)
        net_income = row.get("NetIncome", None)
        current_assets = row.get("CurrentAssets", None)
        current_liab = row.get("CurrentLiab", None)
        total_assets = row.get("TotalAssets", None)
        total_liab = row.get("TotalLiab", None)
        equity = row.get("Equity", None)
        cash = row.get("Cash", None)
        op_ex = row.get("OperatingExpenses", None)

        # Margins
        r["GrossMargin"] = safe_div(gross_profit, revenue) if revenue else None
        r["NetMargin"] = safe_div(net_income, revenue) if revenue else None

        # Liquidity
        r["CurrentRatio"] = safe_div(current_assets, current_liab) if current_liab else None
        # (Quick ratio, Cash ratio can be added later if data present)
        r["CashRatio"] = safe_div(cash, current_liab) if current_liab and cash is not None else None

        # Leverage
        r["DebtToEquity"] = safe_div(total_liab, equity) if equity else None
        r["DebtToAssets"] = safe_div(total_liab, total_assets) if total_assets else None

        # Runway
        monthly_burn = safe_div(op_ex, 3.0) if op_ex else None  # quarterly → monthly
        r["RunwayMonths"] = safe_div(cash, monthly_burn) if monthly_burn and cash is not None else None

        ratios.append(r)

    ratios_df = pd.DataFrame(ratios)

    # Merge ratios back to result (same index)
    result = pd.concat([result.reset_index(drop=True), ratios_df], axis=1)

    return result


def generate_health_summary(df: pd.DataFrame) -> str:
    """
    Tiny text summary based on last period.
    """
    last = df.iloc[-1]

    lines = []
    lines.append(f"Period analyzed (last): {last.get('Period', 'N/A')}")

    gm = last.get("GrossMargin", None)
    if gm is not None:
        lines.append(f"Gross margin: {gm:.1%}")

    nm = last.get("NetMargin", None)
    if nm is not None:
        lines.append(f"Net margin: {nm:.1%}")

    cr = last.get("CurrentRatio", None)
    if cr is not None:
        if cr < 1:
            lines.append(f"Current ratio: {cr:.2f} (below 1 – potential liquidity risk).")
        else:
            lines.append(f"Current ratio: {cr:.2f} (>= 1 – short-term liquidity looks acceptable).")

    dte = last.get("DebtToEquity", None)
    if dte is not None:
        lines.append(f"Debt-to-equity: {dte:.2f}")

    rw = last.get("RunwayMonths", None)
    if rw is not None:
        lines.append(f"Estimated cash runway: {rw:.1f} months (rough approximation).")

    return "\n".join(lines)
