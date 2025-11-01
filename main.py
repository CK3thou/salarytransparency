import os
import sys

import streamlit as st
import pandas as pd
from utils.data_handler import load_data, save_submission, load_preloaded_data
from utils.visualizations import (
    create_salary_distribution, create_experience_salary_correlation,
    create_industry_salary_box, create_degree_distribution,
    create_top_roles_salary
)
from components.forms import submission_form
from components.filters import country_filter
import os

st.set_page_config(
    page_title="Salary Transparency Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"  # Better for mobile
)

def main():
    # Detect whether the app is being run via `streamlit run` (script run context).
    # When running the script directly with `python main.py`, Streamlit's
    # ScriptRunContext is not available and features like session state
    # will emit repeated warnings. In that case, print an instruction and exit
    # early to avoid noisy logs.
    try:
        # Import locally to avoid import-time side effects when not available
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
    except Exception as e:
        # If we can't get context, still try to run the app
        # This allows the app to work even if context detection fails
        ctx = None
        st.warning(f"Note: Script context detection failed: {e}. App may have limited functionality.")
    # PWA Setup
    st.markdown("""
        <link rel="manifest" href="./static/manifest.json">
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0066cc">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <meta name="apple-mobile-web-app-title" content="SalaryApp">
        <link rel="apple-touch-icon" href="./static/icons/icon-192.png">
        <script>
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                    navigator.serviceWorker.register('./static/sw.js', { scope: './' })
                        .catch(err => console.warn('Service worker registration failed:', err));
                });
            }
        </script>
    """, unsafe_allow_html=True)

    # Mobile-first styles
    st.markdown("""
        <style>
            /* Mobile-first styles */
            @media (max-width: 768px) {
                .main .block-container {
                    padding: 1rem !important;
                }
                .stDataFrame {
                    font-size: 14px;
                }
                .stSelectbox {
                    max-width: 100% !important;
                }
                /* Improve touch targets */
                .stButton > button {
                    min-height: 44px;
                }
                /* Make charts responsive */
                .plotly-chart-container {
                    width: 100% !important;
                }
            }
            /* Hide desktop-only elements on mobile */
            @media (max-width: 768px) {
                .desktop-only {
                    display: none !important;
                }
            }
            /* Native-like app styling */
            body {
                -webkit-tap-highlight-color: transparent;
                -webkit-touch-callout: none;
                -webkit-user-select: none;
                user-select: none;
            }
            /* Table container for mobile */
            .table-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                margin: 1rem -1rem;
                padding: 0 1rem;
            }
            /* Alert and exception tweaks */
            .stAlert { border-radius: 8px; }
            .stException { font-size: 0.9em; overflow-x: auto; white-space: pre-wrap; }
            /* Smooth scrolling */
            .main {
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("Salary Transparency Platform")

    # Load data with error handling
    try:
        # Backfill missing submission dates in new submissions file (one-time maintenance)
        try:
            from utils.data_handler import backfill_new_csv_submission_dates
            backfill_new_csv_submission_dates()
        except Exception:
            pass

        with st.spinner("Loading data..."):
            df = load_data()
        if df.empty:
            st.info("No salary data available yet. Be the first to contribute!")
        else:
            st.success(f"Data loaded successfully: {len(df)} rows")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.exception(e)
        df = pd.DataFrame()

    # Main content
    st.subheader("Submissions")

    if not df.empty:
        # Responsive metrics layout
        metrics = st.columns([1, 1, 1])
        with metrics[0]:
            st.metric("Total Entries", len(df))
        with metrics[1]:
            avg_salary = df['Monthly Gross Salary (in ZMW)'].mean()
            st.metric("Average Salary (ZMW)", f"{avg_salary:,.2f}")
        with metrics[2]:
            unique_roles = len(df['Role'].unique())
            st.metric("Unique Roles", unique_roles)

        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Salary Distribution", "Experience Impact",
            "Industry Analysis", "Education Impact",
            "Role Analysis"
        ])

        with tab1:
            try:
                fig = create_salary_distribution(df)
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            except Exception as e:
                st.error(f"Error creating salary distribution chart: {str(e)}")

        with tab2:
            try:
                fig = create_experience_salary_correlation(df)
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            except Exception as e:
                st.error(f"Error creating experience correlation chart: {str(e)}")

        with tab3:
            try:
                fig = create_industry_salary_box(df)
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            except Exception as e:
                st.error(f"Error creating industry analysis chart: {str(e)}")

        with tab4:
            try:
                fig = create_degree_distribution(df)
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            except Exception as e:
                st.error(f"Error creating degree distribution chart: {str(e)}")

        with tab5:
            try:
                fig = create_top_roles_salary(df)
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            except Exception as e:
                st.error(f"Error creating role analysis chart: {str(e)}")

        # Data table with horizontal scroll on mobile
        st.subheader("Detailed Data")
        try:
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            # Check which columns are available
            available_cols = ['Role', 'Monthly Gross Salary (in ZMW)',
                            'Salary Gross in USD', 'Years of Experience',
                            'Industry', 'Company location (Country)',
                            'Submission Date']
            display_cols = [col for col in available_cols if col in df.columns]
            
            if display_cols:
                display_df = df[display_cols].copy()
                
                # Sort by Submission Date if available
                if 'Submission Date' in display_df.columns:
                    display_df = display_df.sort_values('Submission Date', ascending=False)
                    # Format the date for display
                    display_df['Submission Date'] = pd.to_datetime(display_df['Submission Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No displayable columns found in the data.")
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying data table: {str(e)}")
            st.exception(e)
    else:
        st.info("No salary data available yet. Be the first to contribute!")

    # Mobile-friendly submission form
    with st.expander("Submit Your Salary Data", expanded=False):
        submission_form(save_submission)

    # Load data: combined and preloaded-only (preloaded rows will show Submission Date = 2022-01-01)
    combined_df = load_data()
    preloaded_df = load_preloaded_data()

    st.sidebar.markdown("## Data")
    # Admin utility: backfill missing submission dates in new submissions file
    try:
        if st.sidebar.button("Backfill missing submission dates (2023-08-03..2023-12-31)"):
            from utils.data_handler import backfill_new_csv_submission_dates
            updated = backfill_new_csv_submission_dates()
            st.sidebar.success(f"Backfilled {updated} rows.")
    except Exception as _e:
        st.sidebar.caption("Backfill utility unavailable.")
    if st.sidebar.checkbox("Show preloaded data (salary_data.csv)"):
        st.sidebar.write(f"Preloaded rows: {len(preloaded_df)} — Submission Date set to 2022-01-01")
        st.dataframe(preloaded_df)

    if st.sidebar.checkbox("Show new submissions (new_salary.csv)"):
        # show only new entries
        from utils.data_handler import NEW_CSV
        new_df = combined_df.loc[combined_df["Submission Date"] != pd.to_datetime("2022-01-01")]
        st.sidebar.write(f"New submission rows: {len(new_df)}")
        st.dataframe(new_df)

    if st.sidebar.checkbox("Show combined data"):
        st.sidebar.write(f"Total rows: {len(combined_df)}")
        st.dataframe(combined_df)

if __name__ == "__main__":
    #os.system('taskkill /F /IM streamlit.exe')
    main()