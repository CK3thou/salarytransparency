import streamlit as st
from datetime import datetime
from utils.data_handler import get_locations, get_nationalities, get_industries

# Attempt to import forex-python; if it's not installed, keep the app running
try:
    from forex_python.converter import CurrencyRates
    _HAS_FOREX = True
except Exception:
    CurrencyRates = None
    _HAS_FOREX = False

def get_exchange_rate():
    """Get current exchange rate from USD to ZMW"""
    try:
        if not _HAS_FOREX:
            # forex-python not installed; inform user and return None
            st.warning("Currency conversion unavailable: install 'forex-python' to enable this feature.")
            return None

        c = CurrencyRates()
        rate = c.get_rate('USD', 'ZMW')
        return rate
    except Exception as e:
        st.error(f"Error getting exchange rate: {str(e)}")
        return None

def submission_form(save_callback):
    """Render and handle the salary submission form"""
    # Removed the standalone exchange rate button for a cleaner UI

    # Load location options for dropdowns (cached in data handler if desired)
    _locations = get_locations()
    _location_options = ["Select location"] + _locations
    _nationalities = get_nationalities()
    _nationality_options = ["Select nationality"] + _nationalities
    _industries = get_industries()
    _industry_options = ["Select industry"] + _industries

    with st.form("salary_submission_form"):
        # Use columns for better mobile layout
        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("Role*", key="role_mobile")
            company_location = st.selectbox(
                "Company Location*",
                options=_location_options,
                index=0,
                key="location_mobile",
            )
            
            # Salary input in local currency (see Currency Code column in table)
            salary_zmw = st.number_input(
                "Monthly Gross Salary*",
                min_value=0.0,
                step=100.0,
            )
            
            experience = st.number_input(
                "Years of Experience*",
                min_value=0,
                value=0,
                key="experience_mobile"
            )

        with col2:
            degree = st.selectbox(
                "Do you have a degree?*",
                options=["Yes", "No"],
                key="degree_mobile"
            )
            employees = st.number_input(
                "Company Size*",
                min_value=1,
                value=1,
                key="employees_mobile"
            )
            your_location = st.selectbox(
                "Your Location*",
                options=_location_options,
                index=0,
                key="your_location_mobile",
            )
            nationality = st.selectbox(
                "Nationality*",
                options=_nationality_options,
                index=0,
                key="nationality_mobile",
            )
            industry = st.selectbox(
                "Industry*",
                options=_industry_options,
                index=0,
                key="industry_mobile",
            )

        st.markdown("""
            <style>
                div[data-testid="stForm"] {
                    padding: 1rem;
                    border-radius: 10px;
                }
                div[data-testid="stFormSubmitButton"] {
                    margin-top: 1rem;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("*Required fields")
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Treat the sentinel choice as empty so validation works as before
            if company_location == "Select location":
                company_location = ""
            if your_location == "Select location":
                your_location = ""
            # You can do conversion logic here after submission
            if company_location == "Select location":
                company_location = ""
            if your_location == "Select location":
                your_location = ""
            if nationality == "Select nationality":
                nationality = ""
            if company_location == "Select location":
                company_location = ""
            if your_location == "Select location":
                your_location = ""
            if nationality == "Select nationality":
                nationality = ""
            if industry == "Select industry":
                industry = ""
            missing_fields = []
            if not role:
                missing_fields.append("Role")
            if not company_location:
                missing_fields.append("Company Location")
            if not salary_zmw:
                missing_fields.append("Monthly Gross Salary")
            if not experience:
                missing_fields.append("Years of Experience")
            if not your_location:
                missing_fields.append("Your Location")
            if not nationality:
                missing_fields.append("Nationality")
            if not industry:
                missing_fields.append("Industry")
            if missing_fields:
                st.error(f"Please fill in all required fields. Missing: {', '.join(missing_fields)}")
                return False

            data = {
                'Role': role,
                'Company location (Country)': company_location,
                'Monthly Gross Salary': salary_zmw,
                # No direct USD input; USD will be derived in-app using FX rates
                'Years of Experience': experience,
                'Degree': degree,
                'Approx. No. of employees in company': employees,
                'Your Country/ Location': your_location,
                'Nationality': nationality,
                'Industry': industry
            }

            if save_callback(data):
                # Store recent submission in session so main app can toast and highlight it
                st.session_state["recent_submission"] = data
                # Also keep a session-local buffer so the row appears immediately
                # even if the deploy environment has a read-only or ephemeral FS
                try:
                    buf = st.session_state.get("local_rows", [])
                    buf.append(dict(data))
                    st.session_state["local_rows"] = buf
                except Exception:
                    pass
                st.success("Thank you for your submission!")
                # Rerun to refresh the main table immediately
                st.rerun()
                return True
            else:
                st.error("An error occurred while saving your submission.")
                return False