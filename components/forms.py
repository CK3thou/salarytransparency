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

    # Place this outside the form
    if st.button("Get Current Exchange Rate"):
        rate = get_exchange_rate()
        if rate:
            st.info(f"Current USD to ZMW rate: {rate:.2f}")

    # Load options for dropdowns (note: locations are now text inputs due to large dataset)
    # _locations = get_locations()  # Commented out - 45k+ items cause performance issues
    # _location_options = ["Select location"] + _locations
    _nationalities = get_nationalities()
    _nationality_options = ["Select nationality"] + _nationalities
    _industries = get_industries()
    _industry_options = ["Select industry"] + _industries

    with st.form("salary_submission_form"):
        # Use columns for better mobile layout
        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("Role*", key="role_mobile")
            company_location = st.text_input(
                "Company Location* (e.g., Lusaka, Zambia)",
                key="location_mobile",
                help="Enter city and country"
            )
            
            # Salary inputs with currency conversion
            salary_zmw = st.number_input(
                "Monthly Salary (ZMW)*",
                min_value=0.0,
                step=100.0,
            )
            
            salary_usd = st.number_input(
                "Salary in USD",
                min_value=0.0,
                value=0.0,
                key="salary_usd_mobile"
                # Remove on_change here
            )
            
            # Function to update USD salary when ZMW changes
            def update_usd_salary():
                rate = get_exchange_rate()
                if rate and salary_zmw > 0:
                    converted_usd = salary_zmw / rate
                    st.session_state.salary_usd_mobile = converted_usd
                    st.info(f"Converted USD amount: {converted_usd:.2f}")
            
            # Function to update ZMW salary when USD changes
            def update_zmw_salary():
                rate = get_exchange_rate()
                if rate and salary_usd > 0:
                    converted_zmw = salary_usd * rate
                    st.session_state.salary_zmw_mobile = converted_zmw
                    st.info(f"Converted ZMW amount: {converted_zmw:.2f}")
            
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
            your_location = st.text_input(
                "Your Location* (e.g., Zambia)",
                key="your_location_mobile",
                help="Enter your country or city"
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
            # Validation: treat "Select..." sentinel values as empty for dropdowns
            if nationality == "Select nationality":
                nationality = ""
            if industry == "Select industry":
                industry = ""
            
            # For text inputs, just strip whitespace
            company_location = company_location.strip() if company_location else ""
            your_location = your_location.strip() if your_location else ""
            
            missing_fields = []
            if not role:
                missing_fields.append("Role")
            if not company_location:
                missing_fields.append("Company Location")
            if not salary_zmw:
                missing_fields.append("Monthly Salary (ZMW)")
            # Experience has min_value=0 and value=0, so it's always valid (0 is acceptable)
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
                'Monthly Gross Salary (in ZMW)': salary_zmw,
                'Salary Gross in USD': salary_usd if salary_usd > 0 else None,
                'Years of Experience': experience,
                'Degree': degree,
                'Approx. No. of employees in company': employees,
                'Your Country/ Location': your_location,
                'Nationality': nationality,
                'Industry': industry
            }

            if save_callback(data):
                st.success("Thank you for your submission!")
                st.rerun()
                return True
            else:
                st.error("An error occurred while saving your submission.")
                return False