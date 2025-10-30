import streamlit as st
from datetime import datetime

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

    with st.form("salary_submission_form"):
        # Use columns for better mobile layout
        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("Role*", key="role_mobile")
            company_location = st.text_input("Company Location*", key="location_mobile")
            
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
            your_location = st.text_input("Your Location*", key="your_location_mobile")
            nationality = st.text_input("Nationality*", key="nationality_mobile")
            industry = st.text_input("Industry*", key="industry_mobile")

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
            # You can do conversion logic here after submission
            if not all([role, company_location, salary_zmw, experience, 
                       your_location, nationality, industry]):
                st.error("Please fill in all required fields.")
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
                return True
            else:
                st.error("An error occurred while saving your submission.")
                return False