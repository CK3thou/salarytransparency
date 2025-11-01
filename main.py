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
    # PWA Setup
    st.markdown("""
        <link rel="manifest" href="static/manifest.json">
        <meta name="theme-color" content="#0066cc">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <meta name="apple-mobile-web-app-title" content="SalaryApp">
        <link rel="apple-touch-icon" href="static/icons/icon-192.png">
        <script>
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                    navigator.serviceWorker.register('/static/sw.js');
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
                -webkit-user-select: none;                cd /workspaces/salarytransparency
                
                # stage all changes and commit (no-op if nothing to commit)
                git add -A
                git commit -m "Save workspace changes" || echo "No changes to commit"
                
                # show resulting repo state
                git status --porcelain -b
                ```cd /workspaces/salarytransparency
                
                # stage all changes and commit (no-op if nothing to commit)
                git add -A
                git commit -m "Save workspace changes" || echo "No changes to commit"
                
                # show resulting repo state
                git status --porcelain -b
                user-select: none;
            }
            /* Smooth scrolling */
            .main {
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("Salary Transparency Platform")

    # Load data with debug information
    st.write("Loading data...")
    df = load_data()
    st.write(f"Data loaded with {len(df)} rows")

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
            st.plotly_chart(
                create_salary_distribution(df),
                use_container_width=True,
                config={'responsive': True}
            )

        with tab2:
            st.plotly_chart(
                create_experience_salary_correlation(df),
                use_container_width=True,
                config={'responsive': True}
            )

        with tab3:
            st.plotly_chart(
                create_industry_salary_box(df),
                use_container_width=True,
                config={'responsive': True}
            )

        with tab4:
            st.plotly_chart(
                create_degree_distribution(df),
                use_container_width=True,
                config={'responsive': True}
            )

        with tab5:
            st.plotly_chart(
                create_top_roles_salary(df),
                use_container_width=True,
                config={'responsive': True}
            )

        # Data table with horizontal scroll on mobile
        st.subheader("Detailed Data")
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        display_df = df[[
            'Role', 'Monthly Gross Salary (in ZMW)',
            'Salary Gross in USD', 'Years of Experience',
            'Industry', 'Company location (Country)',
            'Submission Date'
        ]].sort_values('Submission Date', ascending=False)

        # Format the date for display
        display_df['Submission Date'] = pd.to_datetime(display_df['Submission Date']).dt.strftime('%Y-%m-%d')

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No salary data available yet. Be the first to contribute!")

    # Mobile-friendly submission form
    with st.expander("Submit Your Salary Data", expanded=False):
        submission_form(save_submission)

    # Load data: combined and preloaded-only (preloaded rows will show Submission Date = 2022-01-01)
    combined_df = load_data()
    preloaded_df = load_preloaded_data()

    st.sidebar.markdown("## Data")
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