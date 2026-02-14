# bfa_core/numeric_processing.py

import pandas as pd


def standardize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B1 – Standardization & basic sanity checks.
    """
    df = df.copy()

    numeric_cols = [
        "Revenue", "COGS", "Salaries", "Marketing", "Rent", "OtherOpex",
        "InterestExpense", "TaxExpense",
        "CurrentAssets", "CurrentLiab", "TotalAssets", "TotalLiab", "Equity", "Cash",
        "Headcount", "NewCustomers",
        "MRR_New", "MRR_Expansion", "MRR_Churned", "MRR_Contraction",
        "ARPU", "ChurnRate",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # simple non-negative check for main flows (if present)
    for col in ["Revenue", "COGS", "Salaries", "Marketing", "Rent"]:
        if col in df.columns and (df[col] < 0).any():
            raise ValueError(f"Negative values found in {col}, not allowed for this prototype.")

    return df


def build_income_statement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B2 – Income statement reconstruction.
    """
    result = df.copy()

    # Gross profit
    result["GrossProfit"] = result["Revenue"] - result["COGS"]

    # Operating expenses (prototype)
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
    Stage 2B3 – Core per-period ratios.
    Works even if there's only one period.
    """
    result = df.copy()

    def safe_div(num, den):
        if den in (0, None) or pd.isna(den):
            return None
        return num / den

    ratios = []

    for _, row in result.iterrows():
        r = {}

        revenue = row.get("Revenue")
        gross_profit = row.get("GrossProfit")
        net_income = row.get("NetIncome")
        current_assets = row.get("CurrentAssets")
        current_liab = row.get("CurrentLiab")
        total_assets = row.get("TotalAssets")
        total_liab = row.get("TotalLiab")
        equity = row.get("Equity")
        cash = row.get("Cash")
        op_ex = row.get("OperatingExpenses")
        headcount = row.get("Headcount")
        marketing = row.get("Marketing")
        new_customers = row.get("NewCustomers")
        arpu = row.get("ARPU")
        churn_rate = row.get("ChurnRate")
        mrr_new = row.get("MRR_New")
        mrr_exp = row.get("MRR_Expansion")
        mrr_churn = row.get("MRR_Churned")
        mrr_contr = row.get("MRR_Contraction")

        # 1) Margins
        r["GrossMargin"] = safe_div(gross_profit, revenue) if revenue else None
        r["OperatingMargin"] = safe_div(row.get("OperatingIncome"), revenue) if revenue else None
        r["NetMargin"] = safe_div(net_income, revenue) if revenue else None

        # 2) Liquidity
        r["CurrentRatio"] = safe_div(current_assets, current_liab) if current_liab else None
        r["CashRatio"] = safe_div(cash, current_liab) if current_liab and cash is not None else None

        # 3) Leverage
        r["DebtToEquity"] = safe_div(total_liab, equity) if equity else None
        r["DebtToAssets"] = safe_div(total_liab, total_assets) if total_assets else None

        # 4) Efficiency
        r["AssetTurnover"] = safe_div(revenue, total_assets) if total_assets else None
        r["OpexRatio"] = safe_div(row.get("OperatingExpenses"), revenue) if revenue else None
        r["RevenuePerEmployee"] = safe_div(revenue, headcount) if headcount else None

        # 5) Burn & runway (assume quarterly)
        monthly_burn = safe_div(op_ex, 3.0) if op_ex else None
        r["BurnRateMonthly"] = monthly_burn
        r["RunwayMonths"] = safe_div(cash, monthly_burn) if monthly_burn and cash is not None else None

        # 6) SaaS metrics (if data available)
        # CAC
        if marketing and new_customers:
            r["CAC"] = safe_div(marketing, new_customers)
        else:
            r["CAC"] = None

        # LTV (simple approximation)
        if arpu and churn_rate and churn_rate != 0:
            r["LTV"] = arpu * (1.0 / churn_rate) * (r["GrossMargin"] if r["GrossMargin"] is not None else 1.0)
        else:
            r["LTV"] = None

        if r["LTV"] and r["CAC"]:
            r["LTV_CAC"] = safe_div(r["LTV"], r["CAC"])
        else:
            r["LTV_CAC"] = None

        # SaaS Quick Ratio
        if (mrr_churn or mrr_contr) and (mrr_new or mrr_exp):
            churn_total = (mrr_churn or 0) + (mrr_contr or 0)
            new_total = (mrr_new or 0) + (mrr_exp or 0)
            r["SaaSQuickRatio"] = safe_div(new_total, churn_total) if churn_total else None
        else:
            r["SaaSQuickRatio"] = None

        ratios.append(r)

    ratios_df = pd.DataFrame(ratios)
    result = pd.concat([result.reset_index(drop=True), ratios_df], axis=1)

    return result


def generate_health_summary(df: pd.DataFrame) -> str:
    """
    Simple text summary based on last period.
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
