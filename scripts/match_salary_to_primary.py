import os
import sys
from pathlib import Path
import pandas as pd

# Optional forex conversion
try:
    from forex_python.converter import CurrencyRates  # type: ignore
    _HAS_FOREX = True
except Exception:
    CurrencyRates = None  # type: ignore
    _HAS_FOREX = False

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data' / 'new_salary.csv'


def main() -> int:
    if not CSV_PATH.exists():
        print(f'ERROR: CSV not found: {CSV_PATH}')
        return 1

    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)

    # Ensure canonical column exists
    if 'Monthly Gross Salary' not in df.columns:
        # Try to map legacy names
        for legacy in ['Monthly Gross Salary (in ZMW)', 'Monthly Gross Salary ZMW', 'Monthly Salary (ZMW)']:
            if legacy in df.columns:
                df['Monthly Gross Salary'] = df[legacy]
                break
        else:
            df['Monthly Gross Salary'] = ''

    # Counts
    filled_from_legacy = 0
    converted_from_usd = 0
    usd_copied_no_fx = 0

    # Fill from legacy if any exists
    for legacy in ['Monthly Gross Salary (in ZMW)', 'Monthly Gross Salary ZMW', 'Monthly Salary (ZMW)']:
        if legacy in df.columns:
            mask = df['Monthly Gross Salary'].astype(str).str.strip().eq('') & df[legacy].astype(str).str.strip().ne('')
            if mask.any():
                df.loc[mask, 'Monthly Gross Salary'] = df.loc[mask, legacy]
                filled_from_legacy += int(mask.sum())

    # Convert from USD if ZMW missing and USD present
    if 'Salary Gross in USD' in df.columns:
        usd_series = pd.to_numeric(df['Salary Gross in USD'], errors='coerce')
        mask = df['Monthly Gross Salary'].astype(str).str.strip().eq('') & usd_series.notna()
        if mask.any():
            if _HAS_FOREX:
                try:
                    rate = CurrencyRates().get_rate('USD', 'ZMW')
                except Exception as e:
                    rate = None
                if rate:
                    df.loc[mask, 'Monthly Gross Salary'] = (usd_series[mask] * rate).round(2).astype(str)
                    converted_from_usd = int(mask.sum())
                else:
                    # Fallback: copy USD as text (not ideal, but requested to match entries)
                    df.loc[mask, 'Monthly Gross Salary'] = usd_series[mask].round(2).astype(str)
                    usd_copied_no_fx = int(mask.sum())
            else:
                # No forex-python: copy USD value as-is to match entries
                df.loc[mask, 'Monthly Gross Salary'] = usd_series[mask].round(2).astype(str)
                usd_copied_no_fx = int(mask.sum())

    # Write back
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')

    print('Updated CSV:', CSV_PATH)
    print('Filled from legacy columns:', filled_from_legacy)
    print('Converted from USD (with FX):', converted_from_usd)
    print('Copied USD without FX (no conversion):', usd_copied_no_fx)
    # Show a tiny preview
    cols = [c for c in ['Role', 'Monthly Gross Salary', 'Salary Gross in USD', 'Submission Date'] if c in df.columns]
    print(df[cols].head(8).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
