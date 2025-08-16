import streamlit as st
from display_utils import add_custom_css, display_header, display_team_guidelines
from individual_form import individual_form
from team_form import team_form
from auth_service import initialize_auth, get_user_info
from utils import initialize_session_state
from sheets_service import check_email_exists

def main():
    # Initialize session state
    initialize_session_state()

    # Page configuration
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

    # Initialize authentication
    initialize_auth()

    # Add custom CSS
    add_custom_css()

    # Display header
    display_header()

    # Display About Circle expander always
    with st.expander("About Circle", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            try:
                st.image("assets/executives.png", use_column_width=True)
            except FileNotFoundError:
                st.error("⚠️ Image file 'assets/executives.png' not found. Please ensure the file exists.")
            except Exception as e:
                st.error(f"⚠️ Error loading image: {str(e)}")
        with col2:
            display_team_guidelines()  # Shows circle info since no team selected

    # Get user info
    user_info = get_user_info()

    # Check if form is submitted
    if st.session_state.get("form_submitted", False):
        if st.session_state.get("submission_type") == "individual":
            st.success("🎉 Individual application submitted successfully!")
            if st.session_state.get("email_sent", False):
                st.success("📧 Confirmation email sent to your registered email address!")
            else:
                st.warning("⚠️ Application saved but confirmation email could not be sent.")
        else:
            team_name = st.session_state.get("team_name", "Your Team")
            member_count = st.session_state.get("member_count", 1)
            st.success(f"🎉 Team application submitted successfully!")
            st.success(f"Team: **{team_name}** with **{member_count} members**")
            successful_emails = st.session_state.get("successful_emails", 0)
            total_members = st.session_state.get("member_count", 1)
            if successful_emails == total_members:
                st.success("📧 Confirmation emails sent to all team members!")
            elif successful_emails > 0:
                st.success(f"📧 Confirmation emails sent to {successful_emails} out of {total_members} team members!")
                st.warning("⚠️ Some confirmation emails could not be sent.")
            else:
                st.warning("⚠️ Team application saved but confirmation emails could not be sent.")
        if st.session_state.get("special_message"):
            st.info(st.session_state.special_message)
        st.balloons()
        return

    if user_info:
        # Check if email already exists
        if check_email_exists(user_info["email"]):
            st.success("Your form has already been submitted.")
            st.info("For further details or updates, please contact KSC.")
            return

        st.info("""
        📢 **Important Note:** Students currently in exams are also encouraged to fill this form. 
        We can schedule meetings later as per your convenience and availability.
        """)

        # Team selection
        st.markdown("### 🎯 Select Your Team")
        team = st.selectbox(
            "Choose your preferred team*", 
            [""] + list(st.session_state.data.keys()), 
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
            col1, col2 = st.columns([1, 2])

            with col1:
                display_team_guidelines()

            with col2:
                selected = st.radio(
                    '📝 Registration Type:', 
                    options=['Individual', 'Team'], 
                    horizontal=True,
                    help="Individual: Solo application | Team: Group application (max 5 members)"
                )

                if selected == 'Individual':
                    individual_form(user_info["email"])
                else:
                    team_form(user_info["email"])
    else:
        st.error("⚠️ Please log in with Google to continue.")

if __name__ == "__main__":
    main()