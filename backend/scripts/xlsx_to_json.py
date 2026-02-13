#!/usr/bin/env python3
"""Convert backend/data/source/Omani Banks List.xlsx to backend/data/omani_banks.json."""

import json
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = BACKEND_ROOT / "data" / "source" / "Omani Banks List.xlsx"
JSON_PATH = BACKEND_ROOT / "data" / "omani_banks.json"


def main() -> None:
    df = pd.read_excel(XLSX_PATH, header=None)
    df.columns = ["bank_name", "bank_name_ar", "bic", "short_name"]
    df = df.iloc[1:]  # Skip header row

    banks = []
    for _, row in df.iterrows():
        short_name = str(row["short_name"]).strip()
        bic = str(row["bic"]).strip()
        bank_name = str(row["bank_name"]).strip()
        if short_name in ("Short Name", "") or bic in ("BIC", "") or bank_name in ("Bank Name", ""):
            continue
        banks.append({"short_name": short_name, "bic": bic, "bank_name": bank_name})

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(banks, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(banks)} banks to {JSON_PATH}")


if __name__ == "__main__":
    main()
