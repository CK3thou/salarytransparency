"""This script is deprecated and no longer used.
All FX rate integrations have been replaced with a direct runtime call to
forexrateapi.com in the Streamlit app. No offline fallback is maintained.
"""

import sys

def main() -> int:
    print("update_fx_rates.py is deprecated: FX rates are fetched at runtime by the app.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
