import streamlit as st
import json

def initialize_session_state():
    """Initialize session state variables"""
    if "num_tabs" not in st.session_state:
        st.session_state.num_tabs = 1
    if "selectedTeam" not in st.session_state:
        st.session_state.selectedTeam = None
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "data" not in st.session_state:
        try:
            with open("team_guidelines.json") as f:
                st.session_state.data = json.load(f)
        except FileNotFoundError:
            st.error("⚠️ team_guidelines.json not found. Please ensure the file exists.")
            st.session_state.data = {}
        except Exception as e:
            st.error(f"⚠️ Error loading team_guidelines.json: {str(e)}")
            st.session_state.data = {}
    if "circle_data" not in st.session_state:
        try:
            with open("circle_info.json") as f:
                st.session_state.circle_data = json.load(f)
        except FileNotFoundError:
            st.error("⚠️ circle_info.json not found. Please ensure the file exists.")
            st.session_state.circle_data = {}
        except Exception as e:
            st.error(f"⚠️ Error loading circle_info.json: {str(e)}")
            st.session_state.circle_data = {}

def validate_form_data(name, crn, contact, email):
    """Validate form inputs and return errors using if-else conditions"""
    errors = []
    
    # Validate name
    if not name.strip():
        errors.append("Name is required")
    else:
        name_parts = name.strip().split()
        if len(name_parts) < 2:
            errors.append("Please enter your full name (first and last name)")
        else:
            for part in name_parts:
                if not part.isalpha():
                    errors.append("Name should contain only letters and spaces")

    # Validate CRN
    if not crn.strip():
        errors.append("CRN is required")
    else:
        if not crn.isdigit():
            errors.append("CRN must contain only digits")
        elif len(crn) != 10:
            errors.append("CRN must be exactly 10 digits")
        else:
            year_prefix = crn[:2]
            valid_years = ["77", "78", "79", "80", "81"]
            if year_prefix not in valid_years:
                errors.append("CRN must start with 77, 78, 79, 80, or 81")
            else:
                section_code = crn[2:4]
                if year_prefix == "77" and section_code != "01":
                    errors.append("CRN for year 77 must have section code 01")
                elif year_prefix in ["78", "79", "80", "81"] and section_code not in ["01", "02", "03", "04"]:
                    errors.append("CRN section code must be 01, 02, 03, or 04 for years 78-81")
                else:
                    roll_number = crn[4:]
                    if section_code == "01":
                        if not (1 <= int(roll_number) <= 49):
                            errors.append("Roll number for section 01 must be between 001 and 049")
                    elif section_code == "02":
                        if not (1 <= int(roll_number) <= 97):
                            errors.append("Roll number for section 02 must be between 001 and 097")
                    elif section_code in ["03", "04"]:
                        if not (1 <= int(roll_number) <= 49):
                            errors.append("Roll number for section 03 or 04 must be between 001 and 049")

    # Validate contact
    if not contact.strip():
        errors.append("Contact number is required")
    else:
        if not contact.isdigit():
            errors.append("Contact number must contain only digits")
        elif len(contact) != 10:
            errors.append("Contact number must be exactly 10 digits")
        elif not (contact.startswith("97") or contact.startswith("98")):
            errors.append("Contact number must start with 97 or 98")

    # Validate email
    if not email.strip():
        errors.append("Email is required")
    else:
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address")
        else:
            local, domain = email.split("@", 1)
            if not local or not domain:
                errors.append("Email must have a valid local part and domain")
            elif domain.count(".") < 1:
                errors.append("Email domain must contain at least one dot")
            elif not all(c.isalnum() or c in "._%+-" for c in local):
                errors.append("Email local part can only contain letters, numbers, and ._%+-")
            elif not all(c.isalnum() or c in ".-" for c in domain):
                errors.append("Email domain can only contain letters, numbers, dots, and hyphens")

    return errors

def has_any_field_filled(member_data):
    """Check if any field in member data is filled"""
    return any([
        member_data.get("name", "").strip(),
        member_data.get("crn", "").strip(),
        member_data.get("contact", "").strip(),
        member_data.get("email", "").strip()
    ])

def add_tab():
    """Add a new team member tab"""
    if st.session_state.num_tabs < 5:
        st.session_state.num_tabs += 1

def remove_tab():
    """Remove the last team member tab"""
    if st.session_state.num_tabs > 1:
        st.session_state.num_tabs -= 1