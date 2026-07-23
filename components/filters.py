import pandas as pd


def country_filter(df: pd.DataFrame):
    """Prompt for a country filter from the local terminal."""
    candidates = [
        "Company location (Country)",
        "Company location",
        "Your Country/ Location",
        "country_location",
    ]
    col = next((c for c in candidates if c in df.columns), None)

    if col is None or df.empty:
        return "All"

    countries = df[col].fillna("Unknown").astype(str).str.strip()
    unique = sorted(x for x in pd.unique(countries) if str(x).strip() and str(x).lower() != "nan")
    options = ["All"] + unique

    print("\nFilter by country")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")

    while True:
        selection = input("Choose a country option number [1]: ").strip()
        if not selection:
            return "All"
        try:
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(options):
                return options[selected_index]
        except ValueError:
            pass
        print("Please choose a valid number.")


def industry_filter(df: pd.DataFrame):
    """Prompt for an industry filter from the local terminal."""
    if df.empty or "Industry" not in df.columns:
        return "All Industries"

    industries = df["Industry"].fillna("").astype(str).str.strip()
    unique = sorted(x for x in pd.unique(industries) if str(x).strip() and str(x).lower() != "nan")
    options = ["All Industries"] + unique

    print("\nFilter by industry")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")

    while True:
        selection = input("Choose an industry option number [1]: ").strip()
        if not selection:
            return "All Industries"
        try:
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(options):
                return options[selected_index]
        except ValueError:
            pass
        print("Please choose a valid number.")
