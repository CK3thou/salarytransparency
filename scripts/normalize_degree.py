import os
import sys
import pandas as pd

PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_salary.csv')
PATH = os.path.abspath(PATH)

def main():
    if not os.path.exists(PATH):
        print(f'ERROR: file not found: {PATH}')
        return 1
    try:
        df = pd.read_csv(PATH)
    except Exception as e:
        print('ERROR: failed to read CSV:', e)
        return 2

    if 'Degree' not in df.columns:
        print('No Degree column found; no changes made.')
        return 0

    s = df['Degree']
    mask = s.astype(str).str.strip().str.lower().eq('yes')
    changed = int(mask.sum())
    if changed:
        df.loc[mask, 'Degree'] = 'Yes'
        try:
            df.to_csv(PATH, index=False)
        except Exception as e:
            print('ERROR: failed to write CSV:', e)
            return 3

    print(f'Normalized Degree -> Yes: {changed} rows updated')
    uniques = sorted(pd.unique(df['Degree'].astype(str)))
    print('Unique Degree values after:', uniques)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
