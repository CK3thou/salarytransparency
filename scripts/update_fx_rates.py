"""
Fetch USD-based FX rates and write data/fx_rates_usd.json for offline fallback.
- Primary source: https://api.exchangerate.host/latest?base=USD
- The output maps code_to_usd: CODE -> rate(code->USD)

Run:
  python scripts/update_fx_rates.py
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'fx_rates_usd.json'
URL = 'https://api.exchangerate.host/latest?base=USD'

def main() -> int:
    try:
        with urllib.request.urlopen(URL, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            rates = data.get('rates', {}) or {}
    except Exception as e:
        print(f"ERROR: failed to fetch rates: {e}")
        return 1

    # Convert USD->CODE to CODE->USD by inverting (handle zeros)
    code_to_usd: dict[str, float] = {'USD': 1.0}
    for code, r in rates.items():
        try:
            rv = float(r)
            if rv != 0:
                code_to_usd[str(code).upper()] = 1.0 / rv
        except Exception:
            continue

    payload = {
        'base': 'USD',
        'as_of': date.today().isoformat(),
        'code_to_usd': code_to_usd,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f"Wrote {OUT} with {len(code_to_usd)} codes as of {payload['as_of']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
