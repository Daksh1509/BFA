# run_bfa.py

from pathlib import Path

from bfa_core.extractor import extract_canonical_financials
from bfa_core.numeric_processing import (
    standardize_numeric,
    build_income_statement,
    compute_core_ratios,
    generate_health_summary,
)
from bfa_core.growth_metrics import add_growth_and_rule_of_40


if __name__ == "__main__":
    # Choose input file (can be 1 year only, or multiple years with projections)
    raw_filepath = "data/sample_financials.xlsx"
    analysis_year = 2026  # or None to use current calendar year

    # 1) Extract canonical financials (handles layout, mapping, 1-year vs multi-year)
    df_canon = extract_canonical_financials(
        filepath=raw_filepath,
        mapping_path="data/column_mapping.json",
        analysis_year=analysis_year,
    )

    print("\n=== Canonical table (with Year / IsFuture) ===")
    print(df_canon)

    # 2) Numeric engine
    df_std = standardize_numeric(df_canon)
    df_is = build_income_statement(df_std)
    df_ratios = compute_core_ratios(df_is)
    df_ratios = add_growth_and_rule_of_40(df_ratios)

    print("\n=== Ratios table ===")
    print(df_ratios)

    # 3) Health summary based on last period
    summary = generate_health_summary(df_ratios)
    print("\n=== Health Summary ===")
    print(summary)

    # 4) Save outputs
    Path("outputs").mkdir(exist_ok=True)
    df_ratios.to_csv("outputs/bfa_output_with_ratios.csv", index=False)
    with open("outputs/health_summary.txt", "w") as f:
        f.write(summary)
