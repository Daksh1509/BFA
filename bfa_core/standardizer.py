# bfa_core/standardizer.py

import pandas as pd
from typing import Dict, List
from .schema import CANONICAL_FIELDS


def apply_mapping_and_clean(df_raw: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Stage 1C – Apply mapping & basic cleaning:
    - Create DataFrame with canonical column names
    - Copy data from user's columns
    - Convert numeric fields
    """
    canonical_cols: List[str] = list(CANONICAL_FIELDS.keys())
    df_std = pd.DataFrame(columns=canonical_cols)

    # 1) Fill canonical columns from mapping
    for canonical in canonical_cols:
        if canonical in mapping:
            user_col = mapping[canonical]
            df_std[canonical] = df_raw[user_col]
        else:
            df_std[canonical] = None  # missing -> NaN later

    # 2) Convert numeric fields
    numeric_fields = [
        "Revenue", "COGS", "Salaries", "Marketing", "Rent", "OtherOpex",
        "InterestExpense", "TaxExpense",
        "CurrentAssets", "CurrentLiab", "TotalAssets", "TotalLiab", "Equity", "Cash",
        "Headcount", "NewCustomers",
        "MRR_New", "MRR_Expansion", "MRR_Churned", "MRR_Contraction",
        "ARPU", "ChurnRate",
    ]

    for field in numeric_fields:
        if field in df_std.columns:
            df_std[field] = pd.to_numeric(df_std[field], errors="coerce")

    # 3) Period must exist
    if df_std["Period"].isnull().all():
        raise ValueError("No Period mapping found or all Period values empty. Please map a time column.")

    df_std = df_std[df_std["Period"].notnull()].reset_index(drop=True)

    return df_std
