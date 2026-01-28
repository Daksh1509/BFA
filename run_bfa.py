# run_bfa.py

from pathlib import Path

from bfa_core.intake import load_raw_financial_file, list_columns
from bfa_core.mapping import interactive_column_mapping, save_mapping, load_mapping
from bfa_core.standardizer import apply_mapping_and_clean
from bfa_core.numeric_processing import (
    standardize_numeric,
    build_income_statement,
    compute_core_ratios,
    generate_health_summary,
)


if __name__ == "__main__":
    # --------- Configuration ----------
    raw_filepath = "data/sample_budget.xlsx"
    mapping_filepath = "data/column_mapping.json"
    # ----------------------------------

    # Stage 1A – load raw file
    df_raw = load_raw_financial_file(raw_filepath)
    user_cols = list_columns(df_raw)

    # Try to reuse existing mapping
    mapping = load_mapping(mapping_filepath)

    if mapping is None:
        # Stage 1B – ask user to map columns
        mapping = interactive_column_mapping(user_cols)
        save_mapping(mapping, mapping_filepath)
        print(f"\nMapping saved to {mapping_filepath}")
    else:
        print(f"Loaded existing mapping from {mapping_filepath}")

    # Stage 1C – apply mapping & cleaning
    df_std = apply_mapping_and_clean(df_raw, mapping)

    # Stage 2B – numeric processing
    df_std = standardize_numeric(df_std)
    df_is = build_income_statement(df_std)
    df_ratios = compute_core_ratios(df_is)

    print("=== Canonical data with ratios ===")
    print(df_ratios)

    summary = generate_health_summary(df_ratios)
    print("\n=== Health Summary ===")
    print(summary)

    Path("outputs").mkdir(exist_ok=True)
    df_ratios.to_csv("outputs/bfa_output_with_ratios.csv", index=False)
    with open("outputs/health_summary.txt", "w") as f:
        f.write(summary)
