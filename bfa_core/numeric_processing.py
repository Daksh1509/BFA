# bfa_core/numeric_processing.py

import pandas as pd


def standardize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B1 – Standardization & basic sanity checks.
    Works for any number of periods (even 1).
    """
    df = df.copy()

    numeric_cols = [
        "Revenue", "COGS", "Salaries", "Marketing", "Rent", "OtherOpex",
        "InterestExpense", "TaxExpense",
        "CurrentAssets", "CurrentLiab", "TotalAssets", "TotalLiab", "Equity", "Cash",
        "Headcount", "NewCustomers",
        "MRR_New", "MRR_Expansion", "MRR_Churned", "MRR_Contraction",
        "ARPU", "ChurnRate",
        # Optional extra fields for richer ratios
        "Inventory",
        "BeginningMRR",     # for NDR / Gross retention / MRR churn rates
        "ChurnedMRR",       # optional alias for MRR_Churned
        "GandA",            # General & admin, if provided
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Simple non-negative check for main flows (if present)
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

    # Operating expenses (prototype: Salaries + Marketing + Rent + OtherOpex)
    opx_cols = [c for c in ["Salaries", "Marketing", "Rent", "OtherOpex"] if c in result.columns]
    result["OperatingExpenses"] = result[opx_cols].sum(axis=1)

    # Operating income
    result["OperatingIncome"] = result["GrossProfit"] - result["OperatingExpenses"]

    # EBIT approximation: OperatingIncome + InterestExpense + TaxExpense (if present)
    interest = result.get("InterestExpense", 0).fillna(0)
    tax = result.get("TaxExpense", 0).fillna(0)
    result["EBIT_est"] = result["OperatingIncome"] + interest + tax

    # Simple tax assumption if TaxExpense not provided: 20% of positive OperatingIncome
    if "TaxExpense" not in result.columns or result["TaxExpense"].isna().all():
        tax_rate = 0.20
        result["TaxExpense_est"] = result["OperatingIncome"].apply(
            lambda x: tax_rate * x if x > 0 else 0.0
        )
        result["NetIncome"] = result["OperatingIncome"] - result["TaxExpense_est"]
    else:
        result["NetIncome"] = result["OperatingIncome"] - result["TaxExpense"]

    return result


def compute_core_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2B3 – Extended per-period ratios for IT/SaaS.
    Works even if there's only one period.

    This computes ~30 metrics per period (where fields exist):
      Margins, Liquidity, Leverage, Returns, Efficiency, Cost structure,
      Burn & runway, SaaS unit economics, Retention.
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
        operating_income = row.get("OperatingIncome")
        ebit_est = row.get("EBIT_est")

        current_assets = row.get("CurrentAssets")
        current_liab = row.get("CurrentLiab")
        total_assets = row.get("TotalAssets")
        total_liab = row.get("TotalLiab")
        equity = row.get("Equity")
        cash = row.get("Cash")
        inventory = row.get("Inventory")

        op_ex = row.get("OperatingExpenses")
        marketing = row.get("Marketing")
        salaries = row.get("Salaries")
        gand_a = row.get("GandA")

        headcount = row.get("Headcount")
        new_customers = row.get("NewCustomers")

        interest_expense = row.get("InterestExpense")
        tax_expense = row.get("TaxExpense") if "TaxExpense" in row else row.get("TaxExpense_est")

        arpu = row.get("ARPU")
        churn_rate = row.get("ChurnRate")

        mrr_new = row.get("MRR_New")
        mrr_exp = row.get("MRR_Expansion")
        mrr_churn = row.get("MRR_Churned") or row.get("ChurnedMRR")
        mrr_contr = row.get("MRR_Contraction")
        beginning_mrr = row.get("BeginningMRR")

        # ---------- 1) Margins ----------
        r["GrossMargin"] = safe_div(gross_profit, revenue) if revenue else None
        r["OperatingMargin"] = safe_div(operating_income, revenue) if revenue else None
        r["NetMargin"] = safe_div(net_income, revenue) if revenue else None

        # ---------- 2) Liquidity ----------
        r["CurrentRatio"] = safe_div(current_assets, current_liab) if current_liab else None

        # Quick ratio: (CurrentAssets - Inventory) / CurrentLiab (approx if no inventory)
        if current_liab:
            if pd.notna(inventory):
                r["QuickRatio"] = safe_div(current_assets - inventory, current_liab)
            else:
                r["QuickRatio"] = safe_div(current_assets, current_liab)
        else:
            r["QuickRatio"] = None

        # Cash ratio
        r["CashRatio"] = safe_div(cash, current_liab) if current_liab and cash is not None else None

        # Working capital
        if pd.notna(current_assets) and pd.notna(current_liab):
            r["WorkingCapital"] = current_assets - current_liab
        else:
            r["WorkingCapital"] = None

        # ---------- 3) Leverage & coverage ----------
        r["DebtToEquity"] = safe_div(total_liab, equity) if equity else None
        r["DebtToAssets"] = safe_div(total_liab, total_assets) if total_assets else None

        # Interest coverage: EBIT / InterestExpense
        if interest_expense and interest_expense != 0:
            r["InterestCoverage"] = safe_div(ebit_est, interest_expense)
        else:
            r["InterestCoverage"] = None

        # Simple debt service coverage: OperatingIncome / InterestExpense
        if interest_expense and interest_expense != 0:
            r["DebtServiceCoverage"] = safe_div(operating_income, interest_expense)
        else:
            r["DebtServiceCoverage"] = None

        # ---------- 4) Returns ----------
        r["ROA"] = safe_div(net_income, total_assets) if total_assets else None
        r["ROE"] = safe_div(net_income, equity) if equity else None

        # ---------- 5) Efficiency / cost structure ----------
        r["AssetTurnover"] = safe_div(revenue, total_assets) if total_assets else None
        r["OpexRatio"] = safe_div(op_ex, revenue) if revenue else None
        r["RevenuePerEmployee"] = safe_div(revenue, headcount) if headcount else None

        # Cash / TotalAssets
        r["CashToAssets"] = safe_div(cash, total_assets) if total_assets and cash is not None else None

        # Marketing / Revenue
        r["MarketingRatio"] = safe_div(marketing, revenue) if revenue and marketing is not None else None

        # Salaries / Revenue
        r["SalariesRatio"] = safe_div(salaries, revenue) if revenue and salaries is not None else None

        # G&A / Revenue
        r["GandARatio"] = safe_div(gand_a, revenue) if revenue and gand_a is not None else None

        # ---------- 6) Burn & runway ----------
        monthly_burn = safe_div(op_ex, 3.0) if op_ex else None  # assuming quarterly
        r["BurnRateMonthly"] = monthly_burn
        r["RunwayMonths"] = safe_div(cash, monthly_burn) if monthly_burn and cash is not None else None

        # ---------- 7) SaaS unit economics ----------
        # CAC
        if marketing and new_customers:
            r["CAC"] = safe_div(marketing, new_customers)
        else:
            r["CAC"] = None

        # LTV (simple)
        if arpu and churn_rate and churn_rate != 0:
            gm_for_ltv = r["GrossMargin"] if r["GrossMargin"] is not None else 1.0
            r["LTV"] = arpu * (1.0 / churn_rate) * gm_for_ltv
        else:
            r["LTV"] = None

        # LTV/CAC
        if r["LTV"] and r["CAC"]:
            r["LTV_CAC"] = safe_div(r["LTV"], r["CAC"])
        else:
            r["LTV_CAC"] = None

        # SaaS Quick Ratio (revenue-based)
        if (mrr_churn or mrr_contr) is not None and (mrr_new or mrr_exp) is not None:
            churn_total = (mrr_churn or 0) + (mrr_contr or 0)
            new_total = (mrr_new or 0) + (mrr_exp or 0)
            r["SaaSQuickRatio"] = safe_div(new_total, churn_total) if churn_total else None
        else:
            r["SaaSQuickRatio"] = None

        # ---------- 8) Retention metrics ----------
        if beginning_mrr and beginning_mrr != 0:
            churn_total = (mrr_churn or 0) + (mrr_contr or 0)
            expansion_total = (mrr_exp or 0)

            # Net Dollar Retention
            end_mrr = beginning_mrr + expansion_total - churn_total
            r["NDR"] = safe_div(end_mrr, beginning_mrr)

            # Gross Retention
            r["GrossRetention"] = safe_div(beginning_mrr - churn_total, beginning_mrr)

            # Gross MRR Churn Rate
            r["GrossMRRChurnRate"] = safe_div(churn_total, beginning_mrr)

            # Expansion MRR Rate
            r["ExpansionMRRRate"] = safe_div(expansion_total, beginning_mrr)

            # Contraction MRR Rate
            r["ContractionMRRRate"] = safe_div((mrr_contr or 0), beginning_mrr)

            # Net MRR Churn Rate (negative of NDR change)
            # Net change = (Expansion + New) - (Churn + Contraction)
            net_change = (mrr_new or 0) + expansion_total - churn_total
            r["NetMRRChurnRate"] = -safe_div(net_change, beginning_mrr)
        else:
            r["NDR"] = None
            r["GrossRetention"] = None
            r["GrossMRRChurnRate"] = None
            r["ExpansionMRRRate"] = None
            r["ContractionMRRRate"] = None
            r["NetMRRChurnRate"] = None

        # ---------- 9) CAC Payback Period ----------
        # Approx: CAC / (ARPU * GrossMargin)
        if r["CAC"] and arpu and r["GrossMargin"] not in (None, 0):
            r["CACPaybackMonths"] = safe_div(r["CAC"], arpu * r["GrossMargin"])
        else:
            r["CACPaybackMonths"] = None

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

    roa = last.get("ROA", None)
    if roa is not None:
        lines.append(f"ROA: {roa:.1%}")

    roe = last.get("ROE", None)
    if roe is not None:
        lines.append(f"ROE: {roe:.1%}")

    return "\n".join(lines)
