# bfa_core/intake.py

import os
import pandas as pd
from typing import List

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


def load_raw_financial_file(filepath: str) -> pd.DataFrame:
    """
    Stage 1A – Load raw file and return DataFrame with original column names.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Use .csv or .xlsx")

    if ext == ".csv":
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    if df.empty:
        raise ValueError("File is empty – no rows found.")

    return df


def list_columns(df: pd.DataFrame) -> List[str]:
    """
    Helper to list columns present in the user's file.
    """
    return list(df.columns)
