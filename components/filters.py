import streamlit as st
import pandas as pd

def country_filter(df: pd.DataFrame):
    """
    Robust country filter: accept several possible column names used in the CSV/data handler.
    Returns the selected country string (or "All").
    """
    candidates = [
        "Company location (Country)",
        "Company location",
        "Your Country/ Location",
        "country_location"
    ]
    col = next((c for c in candidates if c in df.columns), None)

    if col is None or df.empty:
        return "All"

    countries = df[col].fillna("Unknown").astype(str).str.strip()
    # remove empty/"nan" entries and sort
    unique = sorted(x for x in pd.unique(countries) if str(x).strip() and str(x).lower() != "nan")
    options = ["All"] + unique
    selected = st.sidebar.selectbox("Filter by country", options, index=0)
    return selected

def industry_filter(df: pd.DataFrame):
    """
    Industry filter: returns the selected industry string (or "All Industries").
    """
    if df.empty or "Industry" not in df.columns:
        return "All Industries"
    
    industries = df["Industry"].fillna("").astype(str).str.strip()
    # remove empty/"nan" entries and sort
    unique = sorted(x for x in pd.unique(industries) if str(x).strip() and str(x).lower() != "nan")
    options = ["All Industries"] + unique
    selected = st.selectbox(
        "🏢 Filter by Industry",
        options=options,
        index=0,
        key="industry_filter_main"
    )
    return selected