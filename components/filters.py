import streamlit as st

def country_filter(df):
    """Render country selection filter"""
    # Fill NaN values with 'Unknown' and convert to string
    countries = df['Company location (Country)'].fillna('Unknown').astype(str)
    countries = sorted(countries.unique())

    # Add "All Countries" option
    if len(countries) > 0:
        countries = ['All Countries'] + list(countries)
    else:
        countries = ['All Countries']

    selected_country = st.selectbox(
        "Select a country to view salary data:",
        options=countries,
        index=0
    )

    if selected_country == 'All Countries' or selected_country == 'Unknown':
        return None
    return selected_country