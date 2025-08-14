import streamlit as st
import json 
import re
import os
import time
from datetime import datetime
from email_service import send_confirmation_email

FILE = "team_guidelines.json"
INDIVIDUAL_RESPONSES_FILE = "individual_responses.json"
TEAM_RESPONSES_FILE = "team_responses.json"
CIRCLE_INFO_FILE = "circle_info.json"

# Load team guidelines
with open(FILE) as f:
    data = json.load(f)

# Load circle and executive info
with open(CIRCLE_INFO_FILE) as f:
    circle_data = json.load(f)

# Initialize session state
if "num_tabs" not in st.session_state:
    st.session_state.num_tabs = 1
if "selectedTeam" not in st.session_state:
    st.session_state.selectedTeam = None
if "show_exec_modal" not in st.session_state:
    st.session_state.show_exec_modal = True  # Show on initial load
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

def add_custom_css():
    """Add custom CSS for better mobile experience and clean styling"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main-container {
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #007bff;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #007bff;
    }
    
    .main-subtitle {
        font-size: 1rem;
        color: #666;
    }
    
    /* Executive modal styling */
    .exec-modal {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .exec-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #007bff;
    }
    
    .exec-name {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
        color: #333;
    }
    
    .exec-role {
        font-size: 0.9rem;
        color: #007bff;
        margin-bottom: 0.2rem;
    }
    
    .exec-contact {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Form styling */
    .form-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    /* Team guidelines styling */
    .team-guidelines {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .guideline-section {
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 6px;
        border-left: 3px solid #007bff;
    }
    
    /* Close button styling */
    .close-btn {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-size: 16px;
        line-height: 1;
    }
    
    /* Center button styling */
    .center-btn-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    /* Delete button styling */
    .delete-button {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.5rem;
        }
        
        .exec-modal {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .exec-card {
            padding: 0.8rem;
        }
        
        .form-container {
            padding: 1rem;
        }
        
        .team-guidelines {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """Display the main header with gradient background"""
    st.markdown("""
    <div class="main-container">
        <div class="main-header">
            <div class="main-title">🌟 Knowledge Sharing Circle</div>
            <div class="main-subtitle">Join Our Community • Share Knowledge • Grow Together</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_executive_modal():
    """Display executive members modal using Streamlit components"""
    if st.session_state.show_exec_modal:
        with st.container():
            # Close button at top right
            col1, col2, col3 = st.columns([4, 1, 1])
            with col3:
                if st.button("✖️ Close", key="close_exec_modal", use_container_width=True):
                    st.session_state.show_exec_modal = False
                    st.rerun()
            
            st.markdown("### 👥 Meet Our Executive Team")
            st.markdown("---")
            
            # Create executive cards in a grid
            exec_list = list(circle_data["executive_members"].items())
            
            for i in range(0, len(exec_list), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    if i + j < len(exec_list):
                        position, member_info = exec_list[i + j]
                        
                        with col:
                            with st.container():
                                st.markdown(f"**{member_info['name']}**")
                                st.markdown(f"*{position}*")
                                st.write(f"📧 {member_info['contact']}")
                                st.write(f"🎓 {member_info['department']}")
                                st.caption(member_info['role_description'])
                                st.markdown("---")

def display_exec_toggle_button():
    """Display centered button to show executive info"""
    if not st.session_state.show_exec_modal:
        st.markdown('<div class="center-btn-container">', unsafe_allow_html=True)
        if st.button("👥 View Executive Members", key="show_exec_btn", help="View the info about Executive Members",use_container_width=True):
            st.session_state.show_exec_modal = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def load_responses(file_path):
    """Load existing responses from JSON file"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Ensure we always return a list
                if isinstance(data, dict):
                    return []  # Reset if corrupted
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def save_response(file_path, response_data):
    """Save response to JSON file"""
    responses = load_responses(file_path)
    responses.append(response_data)
    with open(file_path, 'w') as f:
        json.dump(responses, f, indent=2)

def add_tab():
    if st.session_state.num_tabs < 5:  # Max 5 members
        st.session_state.num_tabs += 1

def remove_tab():
    if st.session_state.num_tabs > 1:  # Minimum 1 member
        st.session_state.num_tabs -= 1

def validate_form_data(name, crn, contact, email):
    """Validate form inputs and return errors"""
    errors = []
    
    if not name.strip():
        errors.append("Name is required")
    elif not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)+$", name.strip()):
        errors.append("Please enter your full name (first and last name)")
    
    if not crn.strip():
        errors.append("CRN is required")
    elif not re.match(r"^(?:77(?=01(0[1-9]|[1-3][0-9]|4[0-9]))|(?:78|79|80|81)(?:01(0[1-9]|[1-3][0-9]|4[0-9])|02(0[1-9]|[1-8][0-9]|9[0-7])|0[34](0[1-9]|[1-3][0-9]|4[0-9])))$", crn):
        errors.append("Please enter a valid CRN")
    
    if not contact.strip():
        errors.append("Contact number is required")
    elif not re.match(r"^(97|98)\d{8}$", contact):
        errors.append("Please enter a valid contact number (10 digits starting with 97 or 98)")
    
    if not email.strip():
        errors.append("Email is required")
    elif not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        errors.append("Please enter a valid email address")
    
    return errors

def has_any_field_filled(member_data):
    """Check if any field in member data is filled"""
    return any([
        member_data.get("name", "").strip(),
        member_data.get("crn", "").strip(),
        member_data.get("contact", "").strip(),
        member_data.get("email", "").strip()
    ])

def display_team_guidelines():
    """Display team guidelines using Streamlit components"""
    if st.session_state.selectedTeam:
        team_info = data[st.session_state.selectedTeam]
        
        with st.container():
            st.markdown("### 📋 " + st.session_state.selectedTeam)
            
            # Why Join section
            with st.expander("✨ Why Join?", expanded=True):
                st.write(team_info["Why Join"])
            
            # Key Responsibilities section
            with st.expander("🎯 Key Responsibilities", expanded=True):
                for responsibility in team_info["Key Responsibilities"]:
                    st.write(f"• {responsibility}")
            
            # Why Avoid section
            with st.expander("⚠️ Why Avoid?", expanded=True):
                st.write(team_info["Why Avoid"])
    else:
        # Show circle info when no team is selected
        with st.container():
            st.markdown("### 🌟 Knowledge Sharing Circle")
            
            # About Us section
            with st.expander("📖 About Us", expanded=True):
                st.write(circle_data["circle_info"]["about"])
            
            # Mission section
            with st.expander("🎯 Our Mission", expanded=True):
                for mission_item in circle_data["circle_info"]["mission"]:
                    st.write(f"• {mission_item}")
            
            # Vision section
            with st.expander("🔮 Vision", expanded=True):
                st.write(circle_data["circle_info"]["vision"])

def individual_form():
    """Individual form submission with comments field"""
    with st.form("individual_form"):
        st.markdown("### 👤 Individual Registration")
        
        # Use columns for better mobile layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            name = st.text_input("👤 Full Name*", placeholder="Enter your full name")
            crn = st.text_input("🆔 CRN*", placeholder="Enter your CRN")
        
        with col2:
            contact = st.text_input("📱 Contact*", placeholder="97xxxxxxxx or 98xxxxxxxx")
            email = st.text_input("📧 Email*", placeholder="your.email@domain.com")
        
        # Comments field
        comments = st.text_area(
            "💬 Comments / Feedback / Suggestions (Optional)", 
            placeholder="Share any thoughts, suggestions, or feedback you'd like us to know...",
            help="This field is optional. Feel free to share any thoughts or suggestions!"
        )
        
        submit_button = st.form_submit_button("🚀 Submit Individual Application", use_container_width=True)
        
        if submit_button:
            if not st.session_state.selectedTeam:
                st.error("❌ Please select a team first!")
                return
                
            errors = validate_form_data(name, crn, contact, email)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                response_data = {
                    "submission_type": "individual",
                    "timestamp": datetime.now().isoformat(),
                    "name": name.strip(),
                    "crn": crn,
                    "contact": contact,
                    "email": email.lower(),
                    "selected_team": st.session_state.selectedTeam,
                    "comments": comments.strip() if comments else ""
                }
                
                save_response(INDIVIDUAL_RESPONSES_FILE, response_data)
                
                # Send confirmation email
                try:
                    email_sent = send_confirmation_email(
                        recipient_email=email.lower(),
                        recipient_name=name.strip(),
                        team_name=st.session_state.selectedTeam,
                        submission_type="Individual"
                    )
                    if email_sent:
                        st.success("🎉 Individual application submitted successfully!")
                        st.success("📧 Confirmation email sent to your registered email address!")
                    else:
                        st.success("🎉 Individual application submitted successfully!")
                        st.warning("⚠️ Application saved but confirmation email could not be sent.")
                except Exception as e:
                    st.success("🎉 Individual application submitted successfully!")
                    st.warning("⚠️ Application saved but confirmation email could not be sent.")
                    st.error(f"Email error: {str(e)}")
                
                st.balloons()
                st.session_state.form_submitted = True

def team_form():
    """Team form submission with comments field and delete member functionality"""
    with st.form("team_form"):
        st.markdown("### 👥 Team Registration")
        
        team_name = st.text_input("🏆 Team Name*", placeholder="Enter your team name")
        
        st.markdown("#### Team Members (Max 5)")
        
        members_data = []
        
        for i in range(st.session_state.num_tabs):
            st.markdown(f"**👤 Member {i+1}**")
            
            # Mobile-friendly layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                name = st.text_input("Full Name*", key=f"team_name_{i}", placeholder="Full Name")
                crn = st.text_input("CRN*", key=f"team_crn_{i}", placeholder="Your CRN")
            
            with col2:
                contact = st.text_input("Contact*", key=f"team_contact_{i}", placeholder="97xxxxxxxx")
                email = st.text_input("Email*", key=f"team_email_{i}", placeholder="email@domain.com")
            
            members_data.append({
                "name": name,
                "crn": crn,
                "contact": contact,
                "email": email
            })
            
            if i < st.session_state.num_tabs - 1:
                st.markdown("---")
        
        # Team member control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.num_tabs < 5:
                if st.form_submit_button("➕ Add Team Member", use_container_width=True):
                    add_tab()
                    st.rerun()
        
        with col2:
            if st.session_state.num_tabs > 1:
                if st.form_submit_button("🗑️ Remove Last Member", use_container_width=True):
                    remove_tab()
                    st.rerun()
        
        st.markdown("---")
        
        # Comments field for team
        comments = st.text_area(
            "💬 Team Comments / Feedback / Suggestions (Optional)", 
            placeholder="Share any thoughts, suggestions, or feedback about your team application...",
            help="This field is optional. Feel free to share any thoughts or suggestions!"
        )
        
        submit_button = st.form_submit_button("🚀 Submit Team Application", use_container_width=True)
        
        if submit_button:
            if not team_name.strip():
                st.error("❌ Please enter a team name")
                return
                
            if not st.session_state.selectedTeam:
                st.error("❌ Please select a team role first!")
                return
            
            # Check for members with partial data
            valid_members = []
            team_errors = []
            members_with_partial_data = []
            
            for i, member in enumerate(members_data):
                has_data = has_any_field_filled(member)
                
                if has_data:
                    errors = validate_form_data(
                        member["name"], member["crn"], 
                        member["contact"], member["email"]
                    )
                    
                    if errors:
                        team_errors.extend([f"Member {i+1}: {error}" for error in errors])
                        members_with_partial_data.append(i+1)
                    else:
                        valid_members.append({
                            "name": member["name"].strip(),
                            "crn": member["crn"],
                            "contact": member["contact"],
                            "email": member["email"].lower()
                        })
            
            # Provide specific error messages
            if not valid_members and not members_with_partial_data:
                st.error("❌ Please add at least one complete team member with all required fields filled")
                return
            elif not valid_members and members_with_partial_data:
                st.error("❌ Please complete all required fields for the team members you've started filling")
                return
                
            if team_errors:
                st.error("❌ Please fix the following errors:")
                for error in team_errors:
                    st.error(f"   • {error}")
            else:
                response_data = {
                    "submission_type": "team",
                    "timestamp": datetime.now().isoformat(),
                    "team_name": team_name.strip(),
                    "selected_team": st.session_state.selectedTeam,
                    "members": valid_members,
                    "member_count": len(valid_members),
                    "comments": comments.strip() if comments else ""
                }
                
                save_response(TEAM_RESPONSES_FILE, response_data)
                
                # Send confirmation emails to all team members
                email_results = []
                for member in valid_members:
                    try:
                        email_sent = send_confirmation_email(
                            recipient_email=member["email"],
                            recipient_name=member["name"],
                            team_name=st.session_state.selectedTeam,
                            submission_type="Team",
                            team_details={
                                "team_name": team_name.strip(),
                                "member_count": len(valid_members)
                            }
                        )
                        email_results.append(email_sent)
                    except Exception as e:
                        email_results.append(False)
                        st.error(f"Email error for {member['name']}: {str(e)}")
                
                st.success(f"🎉 Team application submitted successfully!")
                st.success(f"Team: **{team_name}** with **{len(valid_members)} members**")
                
                # Email status feedback
                successful_emails = sum(email_results)
                if successful_emails == len(valid_members):
                    st.success("📧 Confirmation emails sent to all team members!")
                elif successful_emails > 0:
                    st.success(f"📧 Confirmation emails sent to {successful_emails} out of {len(valid_members)} team members!")
                    st.warning("⚠️ Some confirmation emails could not be sent.")
                else:
                    st.warning("⚠️ Team application saved but confirmation emails could not be sent.")
                
                st.balloons()
                st.session_state.form_submitted = True

def main():
    # Page configuration for wide mode and mobile optimization
    st.set_page_config(
        page_title="Knowledge Sharing Circle - Team Selection",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'About': "Knowledge Sharing Circle - Building communities through shared learning",
            'Report a bug': None,
            'Get Help': 'mailto:support@knowledgesharingcircle.org'
        }
    )
    
    # Add custom CSS
    add_custom_css()
    
    # Display header
    display_header()
    
    # Executive toggle button
    display_exec_toggle_button()
    
    # Executive modal (shown on initial load)
    display_executive_modal()
    
    # Important note
    if not st.session_state.show_exec_modal:
        st.info("""
        📢 **Important Note:** Students currently in exams are also encouraged to fill this form. 
        We can schedule meetings later as per your convenience and availability.
        """)
        
        # Team selection
        st.markdown("### 🎯 Select Your Team")
        team = st.selectbox(
            "Choose your preferred team*", 
            [""] + list(data.keys()), 
            key="team_selectbox",
            help="Select the team you want to join. Guidelines will appear on the right."
        )
        
        if team != st.session_state.selectedTeam:
            st.session_state.selectedTeam = team
        
        if st.session_state.selectedTeam:
            st.success(f"Please Review the guidelines for **{st.session_state.selectedTeam}**")
        else:
            st.warning("⚠️ Please select a team to continue")
        
        st.markdown("---")
        
        # Create responsive columns - Guidelines LEFT, Forms RIGHT
        if st.session_state.selectedTeam:  # Only show forms if team is selected
            # For mobile, guidelines appear first (top), then forms
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Guidelines on the left (mobile: top)
                display_team_guidelines()
            
            with col2:
                # Registration type selection
                selected = st.radio(
                    '📝 Registration Type:', 
                    options=['Individual', 'Team'], 
                    horizontal=True,
                    help="Individual: Solo application | Team: Group application (max 5 members)"
                )
                
                # Display appropriate form
                if selected == 'Individual':
                    individual_form()
                else:
                    team_form()
        
        else:
            # Show only circle info when no team is selected
            display_team_guidelines()

if __name__ == "__main__":
    main()