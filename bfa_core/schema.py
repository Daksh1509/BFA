# bfa_core/schema.py

CANONICAL_FIELDS = {
    "Period": "Period (time label: Q1-2026, 2026-01, etc.)",

    # Income statement related
    "Revenue": "Total revenue / sales",
    "COGS": "Cost of goods sold / direct costs",
    "Salaries": "Payroll / staff costs",
    "Marketing": "Sales & marketing spend",
    "Rent": "Office / infrastructure rent",
    "OtherOpex": "Other operating expenses (optional)",
    "InterestExpense": "Interest on debt (optional)",
    "TaxExpense": "Tax expense (optional, we can also estimate)",

    # Balance sheet related
    "CurrentAssets": "Current assets",
    "CurrentLiab": "Current liabilities",
    "TotalAssets": "Total assets",
    "TotalLiab": "Total liabilities",
    "Equity": "Shareholders' equity",
    "Cash": "Cash and cash equivalents",

    # SaaS / IT optional fields
    "Headcount": "Number of employees (optional)",
    "NewCustomers": "New customers in period (optional)",
    "MRR_New": "New MRR in period (optional)",
    "MRR_Expansion": "Expansion MRR (optional)",
    "MRR_Churned": "Churned MRR (optional)",
    "MRR_Contraction": "Contraction MRR (optional)",
    "ARPU": "Average revenue per user (optional)",
    "ChurnRate": "Customer churn rate (optional)",
}
