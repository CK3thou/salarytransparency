import os
import sys

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from utils.data_handler import load_data, save_submission
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
    
    # Google Analytics - inject into page head using full HTML document
    GOOGLE_ANALYTICS_CODE = """
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-62K86SX2TC"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-62K86SX2TC');
        </script>
        <script>
          // Send to parent window to ensure tracking works
          if (window.parent) {
            window.parent.dataLayer = window.parent.dataLayer || [];
            function parentGtag(){window.parent.dataLayer.push(arguments);}
            parentGtag('js', new Date());
            parentGtag('config', 'G-62K86SX2TC');
          }
        </script>
    </head>
    <body></body>
    </html>
    """
    components.html(GOOGLE_ANALYTICS_CODE, height=0, width=0)

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

    @st.cache_data(show_spinner=False)
    def load_currency_map():
        """Load mapping of Location -> Currency Code from data/worldcities.csv."""
        try:
            path = os.path.join('data', 'worldcities.csv')
            wdf = pd.read_csv(path, dtype=str)
            wdf = wdf[['Location', 'Currency Code']].dropna()
            wdf['Location'] = wdf['Location'].astype(str).str.strip().str.lower()
            # Normalize currency code to first 3-letter token (handle slashes/parentheses)
            def norm_code(x: str) -> str:
                x = str(x)
                # remove text in parentheses
                if '(' in x:
                    x = x.split('(')[0]
                # split by slash or comma and take first
                for sep in ['/', ',']:
                    if sep in x:
                        x = x.split(sep)[0]
                x = x.strip().upper()
                # take only 3-letter code if longer
                if len(x) >= 3:
                    x = x[:3]
                return x
            wdf['Currency Code'] = wdf['Currency Code'].map(norm_code)
            wdf = wdf.drop_duplicates(subset=['Location'])
            return dict(zip(wdf['Location'], wdf['Currency Code']))
        except Exception:
            return {}

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
            # Session-local pending rows (in case writes are ephemeral on cloud)
            try:
                pending = st.session_state.get("local_rows", [])
                if pending:
                    add_df = pd.DataFrame(pending)
                    # Minimal normalization to expected columns
                    # Keep only known columns, add missing ones as blanks
                    expected = [
                        'Role','Company location','Company location (Country)','Monthly Gross Salary',
                        'Salary Gross in USD','Years of Experience','Degree',
                        'Approx. No. of employees in company','Your Country/ Location',
                        'Nationality','Industry','Submission Date','Real-time USD ZMW exchange rate'
                    ]
                    for c in expected:
                        if c not in add_df.columns:
                            add_df[c] = ''
                    add_df = add_df[expected].copy()
                    # Coerce date to dd/mm/YYYY display format
                    add_df['Submission Date'] = pd.to_datetime(
                        add_df['Submission Date'], errors='coerce', dayfirst=True
                    ).dt.strftime('%d/%m/%Y')
                    # Coerce numeric
                    add_df['Monthly Gross Salary'] = pd.to_numeric(add_df['Monthly Gross Salary'], errors='coerce')
                    add_df['Salary Gross in USD'] = pd.to_numeric(add_df['Salary Gross in USD'], errors='coerce')
                    # Prefer the explicit country column for display compatibility
                    mask_missing_country = add_df['Company location (Country)'].astype(str).str.strip().eq('')
                    add_df.loc[mask_missing_country, 'Company location (Country)'] = add_df.loc[mask_missing_country, 'Company location']
                    # Combine for display
                    df = pd.concat([df, add_df], ignore_index=True)
            except Exception:
                pass
        if df.empty:
            st.info("No salary data available yet. Be the first to contribute!")
        else:
            st.success(f"Data loaded successfully: {len(df)} rows")
            # Derive a Currency Code column based on user's location selections
            try:
                currency_lookup = load_currency_map()
                if currency_lookup:
                    candidates = []
                    for col in ['Your Country/ Location', 'Company location (Country)', 'Company location']:
                        if col in df.columns:
                            s = df[col].astype(str).str.strip().str.lower().map(currency_lookup)
                            candidates.append(s)
                    if candidates:
                        currency_code = candidates[0].copy()
                        for s in candidates[1:]:
                            currency_code = currency_code.fillna(s)
                        df['Currency Code'] = currency_code.fillna('')
            except Exception:
                # Non-fatal if currency map fails
                pass
            # Derive USD equivalent using forexrateapi.com in one batched call (cached)
            @st.cache_data(ttl=21600, show_spinner=False)
            def get_rates_code_to_usd(codes_csv: str) -> dict:
                """Fetch CODE->USD rates using forexrateapi.com with USD base.
                Args:
                    codes_csv: Comma-separated list of 3-letter currency codes to request.
                Returns:
                    { 'rates': { CODE: rate(code->USD), ... }, 'source': 'forexrateapi.com' }
                """
                import json
                import urllib.request
                import urllib.parse

                # API key resolution: prefer secrets/env, fallback to provided key
                api_key = None
                try:
                    # Try flat secret first, then nested
                    api_key = st.secrets.get('forexrateapi_api_key')
                    if not api_key and 'forexrateapi' in st.secrets:
                        api_key = st.secrets['forexrateapi'].get('api_key')
                except Exception:
                    api_key = None
                if not api_key:
                    api_key = os.environ.get('FOREXRATEAPI_API_KEY')
                if not api_key:
                    # Fallback to user-provided key
                    api_key = '1e5ce0b6f7f9b60ffeb7b5f60dcf095d'

                params = {
                    'api_key': api_key,
                    'base': 'USD',
                    'currencies': codes_csv,
                }
                url = 'https://api.forexrateapi.com/v1/latest?' + urllib.parse.urlencode(params, safe=',')

                def _return(inv: dict) -> dict:
                    out = {'USD': 1.0}
                    for k, v in (inv or {}).items():
                        try:
                            if v is None:
                                continue
                            out[str(k).upper()] = float(v)
                        except Exception:
                            continue
                    return {'rates': out, 'source': 'forexrateapi.com'}

                try:
                    with urllib.request.urlopen(url, timeout=4) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        # API returns USD->CODE rates; convert to CODE->USD
                        usd_to_code = data.get('rates', {}) or {}
                        inv = {}
                        for c, r in usd_to_code.items():
                            try:
                                rv = float(r)
                                inv[str(c).upper()] = (1.0 / rv) if rv != 0 else None
                            except Exception:
                                continue
                        return _return(inv)
                except Exception:
                    # Last resort: only USD
                    return _return({'USD': 1.0})

            try:
                # Ensure numeric salary
                if 'Monthly Gross Salary' in df.columns:
                    df['Monthly Gross Salary'] = pd.to_numeric(df['Monthly Gross Salary'], errors='coerce')
                # Compute rates once, then map per row
                if 'Currency Code' in df.columns and 'Monthly Gross Salary' in df.columns:
                    codes = df['Currency Code'].astype(str).str.upper().fillna('')
                    unique_codes = sorted(set([c for c in codes.tolist() if c and c != 'USD']))
                    codes_csv = ','.join(unique_codes)
                    payload = get_rates_code_to_usd(codes_csv)
                    rates_map = payload.get('rates', {})
                    st.session_state['fx_source'] = payload.get('source', '')
                    rates = codes.map(lambda x: rates_map.get(x, None)).astype(float)
                    df['Monthly Salary in USD'] = df['Monthly Gross Salary'] * rates
            except Exception:
                pass
            # If a recent submission exists from the form, show a toast and a compact preview
            if "recent_submission" in st.session_state:
                recent = st.session_state.pop("recent_submission", None)
                if recent:
                    try:
                        role = recent.get("Role", "")
                        loc = recent.get("Company location (Country)", recent.get("Company location", ""))
                        zmw = recent.get("Monthly Gross Salary")
                        zmw_txt = f"{float(zmw):,.2f}" if zmw not in (None, "") else "-"
                        st.toast(f"Added submission: {role} — {zmw_txt} ({loc})", icon="✅")
                        with st.expander("Recently added (just now)", expanded=False):
                            # Compute currency code for the recent preview (best-effort)
                            currency_lookup = load_currency_map()
                            recent_loc = (recent.get('Your Country/ Location') or loc or '').strip().lower()
                            recent_ccy = currency_lookup.get(recent_loc, '') if currency_lookup else ''
                            recent_view = {
                                "Role": role,
                                "Company location (Country)": loc,
                                "Currency Code": recent_ccy,
                                "Monthly Gross Salary": zmw,
                                "Years of Experience": recent.get("Years of Experience", ""),
                                "Industry": recent.get("Industry", ""),
                            }
                            st.dataframe(pd.DataFrame([recent_view]), use_container_width=True, hide_index=True)
                    except Exception:
                        # Non-fatal; continue rendering the page
                        pass
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
            # Average in USD if available
            s = pd.to_numeric(df.get('Monthly Salary in USD'), errors='coerce')
            avg_salary = float(s.mean()) if s is not None and len(s) else 0.0
            st.metric("Average Salary (USD)", f"{avg_salary:,.2f}")
        with metrics[2]:
            unique_roles = len(df['Role'].unique())
            st.metric("Unique Roles", unique_roles)

        # Optional FX source caption for debugging/visibility
        try:
            fx_src = st.session_state.get('fx_source', '')
            if fx_src:
                st.caption(f"Rates: {fx_src} (cached)")
        except Exception:
            pass

        # Data table with horizontal scroll on mobile (all data from new_salary.csv)
        st.subheader("All Data")
        # Hint if FX-derived USD values are missing
        try:
            if 'Monthly Salary in USD' not in df.columns or pd.to_numeric(df.get('Monthly Salary in USD'), errors='coerce').notna().sum() == 0:
                st.info("Live FX rates unavailable or not yet loaded; USD values may be blank.")
        except Exception:
            pass
        try:
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            # Build display DataFrame and ensure Currency Code is inserted before Monthly Gross Salary
            display_df = df.copy()
            if 'Currency Code' not in display_df.columns:
                # Ensure column exists (may be empty if mapping failed)
                display_df['Currency Code'] = ''

            # Desired display order (will filter by availability)
            desired_order = ['Role', 'Currency Code', 'Monthly Gross Salary', 'Monthly Salary in USD',
                             'Years of Experience', 'Industry', 'Nationality', 'Company location (Country)',
                             'Submission Date']
            display_cols = [c for c in desired_order if c in display_df.columns]

            if display_cols:
                display_df = display_df[display_cols].copy()
                
                # Sort by Submission Date if available
                if 'Submission Date' in display_df.columns:
                    display_df = display_df.sort_values('Submission Date', ascending=False)
                    # Format the date for display as dd/mm/YYYY
                    display_df['Submission Date'] = pd.to_datetime(
                        display_df['Submission Date'], errors='coerce', dayfirst=True
                    ).dt.strftime('%d/%m/%Y')
                
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

        # Recommended visualizations (rendered below the table)
        st.subheader("Visualizations")
        try:
            st.markdown("### Salary Distribution")
            fig = create_salary_distribution(df)
            st.plotly_chart(fig, width='stretch', config={'responsive': True})
        except Exception as e:
            st.error(f"Error creating salary distribution chart: {str(e)}")

        try:
            st.markdown("### Experience vs Salary")
            fig = create_experience_salary_correlation(df)
            st.plotly_chart(fig, width='stretch', config={'responsive': True})
        except Exception as e:
            st.error(f"Error creating experience correlation chart: {str(e)}")

        try:
            st.markdown("### Industry Salary Spread")
            fig = create_industry_salary_box(df)
            st.plotly_chart(fig, width='stretch', config={'responsive': True})
        except Exception as e:
            st.error(f"Error creating industry analysis chart: {str(e)}")

        try:
            st.markdown("### Salary by Degree")
            fig = create_degree_distribution(df)
            st.plotly_chart(fig, width='stretch', config={'responsive': True})
        except Exception as e:
            st.error(f"Error creating degree distribution chart: {str(e)}")

        try:
            st.markdown("### Top Roles by Salary")
            fig = create_top_roles_salary(df)
            st.plotly_chart(fig, width='stretch', config={'responsive': True})
        except Exception as e:
            st.error(f"Error creating role analysis chart: {str(e)}")
    else:
        st.info("No salary data available yet. Be the first to contribute!")

    # Mobile-friendly submission form
    with st.expander("Submit Your Salary Data", expanded=False):
        submission_form(save_submission)

    # Sidebar removed per request

if __name__ == "__main__":
    #os.system('taskkill /F /IM streamlit.exe')
    main()