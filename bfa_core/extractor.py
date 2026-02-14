# bfa_core/extractor.py

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import re

from .intake import load_raw_financial_file
from .mapping import interactive_column_mapping, load_mapping, save_mapping
from .schema import CANONICAL_FIELDS


# ---------- 1. Layout detection ----------

def detect_layout(df: pd.DataFrame) -> str:
    """
    Try to recognize the layout of the financial data.
    Returns:
      - 'metrics_by_period'
      - 'annual_balance_sheet'
      - 'unknown'
    """
    cols = list(df.columns)

    # Check metrics-by-period: first col looks like period, rest numeric
    first_col = str(cols[0]).lower()
    if any(x in first_col for x in ["period", "year", "fy", "q"]):
        numeric_cols = sum(pd.api.types.is_numeric_dtype(df[c]) for c in cols[1:])
        if numeric_cols >= 1:
            return "metrics_by_period"

    # Check annual balance sheet: first col items, next cols look like years
    year_like_count = 0
    for c in cols[1:]:
        s = str(c)
        if s.isdigit() and len(s) == 4:
            year_like_count += 1
    if year_like_count >= 1:
        return "annual_balance_sheet"

    return "unknown"


# ---------- 2. Reshaping helpers ----------

def reshape_metrics_by_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Layout: [Period, metric1, metric2, ...]
    """
    df = df.copy()
    df.rename(columns={df.columns[0]: "Period"}, inplace=True)
    df["Period"] = df["Period"].astype(str)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def reshape_annual_balance_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Layout: [Item, 2022, 2023, 2024, ...] -> [Item, Period, Value]
    """
    df = df.copy()
    item_col = df.columns[0]
    period_cols = df.columns[1:]

    df_long = pd.melt(
        df,
        id_vars=[item_col],
        value_vars=period_cols,
        var_name="Period",
        value_name="Value",
    )

    df_long.rename(columns={item_col: "Item"}, inplace=True)
    df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")
    df_long = df_long.dropna(subset=["Value"]).reset_index(drop=True)

    return df_long


# ---------- 3. Manual mapping helper ----------

def get_or_create_mapping(
    keys_to_map: List[str],
    mapping_path: str,
) -> Dict[str, str]:
    """
    Load an existing canonical->key mapping if exists, otherwise ask user.
    """
    existing = load_mapping(mapping_path)
    if existing is not None:
        print(f"Loaded existing mapping from {mapping_path}")
        return existing

    print("\nNo existing mapping found. Let's define it now.")
    mapping = interactive_column_mapping(keys_to_map)
    save_mapping(mapping, mapping_path)
    print(f"\nMapping saved to {mapping_path}")
    return mapping


# ---------- 4. Build canonical table ----------

from .standardizer import apply_mapping_and_clean


def build_canonical_from_metrics_by_period(
    df_metrics: pd.DataFrame,
    mapping: Dict[str, str],
) -> pd.DataFrame:
    """
    metrics-by-period: mapping = canonical -> column
    """
    df_std = apply_mapping_and_clean(df_metrics, mapping)
    return df_std


def build_canonical_from_annual_bs(
    df_long: pd.DataFrame,
    mapping: Dict[str, str],
) -> pd.DataFrame:
    """
    df_long: [Item, Period, Value]
    mapping: canonical_field -> item_label
    Output: one row per Period, columns = canonical fields
    """
    periods = sorted(df_long["Period"].unique())
    canonical_df = pd.DataFrame({"Period": periods})

    for canonical_field, item_label in mapping.items():
        if canonical_field == "Period":
            continue
        rows = df_long[df_long["Item"] == item_label][["Period", "Value"]]
        if rows.empty:
            continue
        series = rows.set_index("Period")["Value"]
        canonical_df[canonical_field] = canonical_df["Period"].map(series)

    return canonical_df


# ---------- 5. Historical vs future tagging ----------

def parse_year_from_period(period_str: str) -> Optional[int]:
    """
    Try to extract a year integer from Period string.
    """
    matches = re.findall(r"\b(20\d{2})\b", period_str)
    if matches:
        return int(matches[0])
    return None


def add_year_and_future_flags(
    df: pd.DataFrame,
    analysis_year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Add Year and IsFuture columns.
    """
    df = df.copy()
    if analysis_year is None:
        analysis_year = datetime.now().year

    years = []
    futures = []

    for p in df["Period"]:
        year = parse_year_from_period(str(p)) or analysis_year
        years.append(year)
        futures.append(year > analysis_year)

    df["Year"] = years
    df["IsFuture"] = futures

    return df


# ---------- 6. Main extractor API ----------

def extract_canonical_financials(
    filepath: str,
    mapping_path: str = "data/column_mapping.json",
    analysis_year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Unified extractor:
    - Load raw file
    - Detect layout
    - Reshape
    - Manual mapping (once)
    - Return canonical table with Period, Year, IsFuture + canonical numeric fields.

    Works for:
    - Only one year
    - Multiple years (past + future)
    """
    df_raw = load_raw_financial_file(filepath)
    layout = detect_layout(df_raw)
    print(f"Detected layout: {layout}")

    if layout == "metrics_by_period":
        df_metrics = reshape_metrics_by_period(df_raw)
        metric_cols = [c for c in df_metrics.columns if c != "Period"]
        mapping = get_or_create_mapping(metric_cols, mapping_path)
        df_canon = build_canonical_from_metrics_by_period(df_metrics, mapping)

    elif layout == "annual_balance_sheet":
        df_long = reshape_annual_balance_sheet(df_raw)
        item_keys = sorted(df_long["Item"].unique().tolist())
        mapping = get_or_create_mapping(item_keys, mapping_path)
        df_canon = build_canonical_from_annual_bs(df_long, mapping)

    else:
        raise ValueError(
            "Unknown layout. Please provide either:\n"
            "- A table with Period in first column and metrics in other columns, OR\n"
            "- A table with Item in first column and years in next columns."
        )

    df_canon = add_year_and_future_flags(df_canon, analysis_year)
    return df_canon
