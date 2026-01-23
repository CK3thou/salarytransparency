import streamlit as st
from datetime import datetime
from utils.data_handler import get_locations, get_nationalities, get_industries

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
            # Guidance: currency must match the "Your Location" field
            st.caption("Enter this amount in the currency of your 'Your Location' selection. We'll convert to USD automatically.")
            
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
                    padding: 2rem;
                    border-radius: 15px;
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                }
                
                div[data-testid="stForm"] label {
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 0.5rem;
                }
                
                div[data-testid="stFormSubmitButton"] {
                    margin-top: 1.5rem;
                }
                
                div[data-testid="stFormSubmitButton"] > button {
                    width: 100%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0.875rem 2rem;
                    font-weight: 600;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
                }
                
                div[data-testid="stFormSubmitButton"] > button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
                }
                
                .stTextInput > div > div > input,
                .stNumberInput > div > div > input,
                .stSelectbox > div > div > select {
                    border-radius: 10px;
                    border: 2px solid #e2e8f0;
                    padding: 0.75rem;
                    transition: all 0.3s ease;
                    background: white;
                    color: black;
                }
                
                .stTextInput > div > div > input:focus,
                .stNumberInput > div > div > input:focus,
                .stSelectbox > div > div > select:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                    outline: none;
                }
                
                .stCaption {
                    color: #718096;
                    font-size: 0.85rem;
                    font-style: italic;
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