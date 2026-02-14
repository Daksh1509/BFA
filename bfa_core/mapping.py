# bfa_core/mapping.py

from typing import Dict, List, Optional
import json
import os

from .schema import CANONICAL_FIELDS


def interactive_column_mapping(user_columns: List[str]) -> Dict[str, str]:
    """
    Stage 1B – Ask the user to map their columns/labels to canonical fields.
    Returns dict: { canonical_field -> user_column_or_item }
    """
    print("\nDetected columns/items in your data:")
    for col in user_columns:
        print(f"  - {col}")

    print("\nNow we will map your data to BFA's standard fields.")
    print("If you don't have a field, just press Enter to skip.\n")

    mapping: Dict[str, str] = {}

    for canonical_name, description in CANONICAL_FIELDS.items():
        prompt = f'Which column/item corresponds to "{canonical_name}" ({description})? '
        user_input = input(prompt).strip()

        if user_input == "":
            continue

        if user_input not in user_columns:
            print(f'  WARNING: "{user_input}" is not in the detected list. Skipping.')
            continue

        mapping[canonical_name] = user_input

    print("\nFinal mapping (canonical -> your column/item):")
    for k, v in mapping.items():
        print(f"  {k} -> {v}")

    return mapping


def save_mapping(mapping: Dict[str, str], filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(mapping, f, indent=2)


def load_mapping(filepath: str) -> Optional[Dict[str, str]]:
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)
