from utils.data_handler import get_locations, get_nationalities, get_industries


def _prompt_text(prompt: str, required: bool = True) -> str:
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("Value is required.")


def _prompt_number(prompt: str, min_value: float = 0.0) -> float:
    while True:
        value = input(prompt).strip()
        try:
            number = float(value)
            if number >= min_value:
                return number
            print(f"Value must be at least {min_value}.")
        except ValueError:
            print("Please enter a valid number.")


def _prompt_choice(prompt: str, options: list[str], sentinel: str | None = None) -> str:
    if not options:
        return ""

    if sentinel is not None:
        options = [sentinel] + options

    while True:
        print(prompt)
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option}")
        selection = input("Choose an option number: ").strip()
        try:
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(options):
                return options[selected_index]
        except ValueError:
            pass
        print("Please choose a valid option.")


def submission_form(save_callback):
    """Collect salary data from the local console and save it."""
    print("\nSubmit a new salary entry")

    locations = get_locations()
    nationalities = get_nationalities()
    industries = get_industries()

    role = _prompt_text("Role*: ")
    company_location = _prompt_choice("Company Location*: ", locations, sentinel="Select location")
    if company_location == "Select location":
        company_location = ""

    salary_zmw = _prompt_number("Monthly Gross Salary*: ")
    experience = _prompt_number("Years of Experience*: ", min_value=0)
    degree = _prompt_choice("Degree*: ", ["Yes", "No"])
    employees = _prompt_number("Approx. No. of employees*: ", min_value=1)
    your_location = _prompt_choice("Your Location*: ", locations, sentinel="Select location")
    if your_location == "Select location":
        your_location = ""

    nationality = _prompt_choice("Nationality*: ", nationalities, sentinel="Select nationality")
    if nationality == "Select nationality":
        nationality = ""

    industry = _prompt_choice("Industry*: ", industries, sentinel="Select industry")
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
        print(f"Please fill in all required fields. Missing: {', '.join(missing_fields)}")
        return False

    data = {
        "Role": role,
        "Company location (Country)": company_location,
        "Monthly Gross Salary": salary_zmw,
        "Years of Experience": experience,
        "Degree": degree,
        "Approx. No. of employees in company": employees,
        "Your Country/ Location": your_location,
        "Nationality": nationality,
        "Industry": industry,
    }

    result = save_callback(data)
    if isinstance(result, tuple):
        success, message = result
    else:
        success = result
        message = "Submission saved!" if success else "Failed to save submission"

    if success:
        print(message)
        return True

    print(message)
    return False
