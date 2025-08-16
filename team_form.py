import streamlit as st
from utils import validate_form_data, has_any_field_filled, add_tab, remove_tab
from email_service import send_confirmation_email
from sheets_service import save_team_response, save_individual_response
from datetime import datetime

def team_form(user_email):
    with st.form("team_form"):
        st.markdown("### 👥 Team Registration")
        
        team_name = st.text_input("🏆 Team Name*", placeholder="Enter your team name")
        
        st.markdown("#### Team Members (Max 5)")
        
        members_data = []
        
        for i in range(st.session_state.num_tabs):
            # Display Team Lead badge for first member
            if i == 0:
                st.markdown("**👤 Team Lead** <span class='team-lead-badge'>LEAD</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**👤 Member {i+1}**")
            
            # Mobile-friendly layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                name = st.text_input("Full Name*", key=f"team_name_{i}", placeholder="Full Name")
                crn = st.text_input("CRN*", key=f"team_crn_{i}", placeholder="Your CRN")
            
            with col2:
                contact = st.text_input("Contact*", key=f"team_contact_{i}", placeholder="97xxxxxxxx")
                email = st.text_input("Email*", key=f"team_email_{i}", value=user_email if i == 0 else "", disabled=(i == 0))
            
            members_data.append({
                "name": name,
                "crn": crn,
                "contact": contact,
                "email": user_email if i == 0 else email
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
                st.error("⚠ Please enter a team name")
                return
                
            if not st.session_state.selectedTeam:
                st.error("⚠ Please select a team role first!")
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
                        member_title = "Team Lead" if i == 0 else f"Member {i+1}"
                        team_errors.extend([f"{member_title}: {error}" for error in errors])
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
                st.error("⚠ Please add at least one complete team member with all required fields filled")
                return
            elif not valid_members and members_with_partial_data:
                st.error("⚠ Please complete all required fields for the team members you've started filling")
                return
                
            if team_errors:
                st.error("⚠ Please fix the following errors:")
                for error in team_errors:
                    st.error(f"   • {error}")
            else:
                if len(valid_members) == 1:
                    # Save as individual
                    response_data = {
                        "submission_type": "individual",
                        "timestamp": datetime.now().isoformat(),
                        "name": valid_members[0]["name"],
                        "crn": valid_members[0]["crn"],
                        "contact": valid_members[0]["contact"],
                        "email": valid_members[0]["email"],
                        "selected_team": st.session_state.selectedTeam,
                        "comments": comments.strip() if comments else ""
                    }
                    
                    sheets_success = save_individual_response(response_data)
                    
                    if sheets_success:
                        # Send confirmation email
                        try:
                            email_sent = send_confirmation_email(
                                recipient_email=valid_members[0]["email"],
                                recipient_name=valid_members[0]["name"],
                                team_name=st.session_state.selectedTeam,
                                submission_type="Individual"
                            )
                            st.session_state.form_submitted = True
                            st.session_state.submission_type = "individual"
                            st.session_state.email_sent = email_sent
                            st.session_state.special_message = "Recorded as individual form since only one member was added."
                            st.rerun()
                        except Exception as e:
                            st.session_state.form_submitted = True
                            st.session_state.submission_type = "individual"
                            st.session_state.email_sent = False
                            st.session_state.special_message = "Recorded as individual form since only one member was added."
                            st.rerun()
                    else:
                        st.error("❌ Failed to save application. Please try again.")
                else:
                    # Save as team
                    response_data = {
                        "submission_type": "team",
                        "timestamp": datetime.now().isoformat(),
                        "team_name": team_name.strip(),
                        "selected_team": st.session_state.selectedTeam,
                        "members": valid_members,
                        "member_count": len(valid_members),
                        "comments": comments.strip() if comments else ""
                    }
                    
                    sheets_success = save_team_response(response_data)
                    
                    if sheets_success:
                        # Send confirmation emails to all team members
                        email_results = []
                        for i, member in enumerate(valid_members):
                            try:
                                # Use different email templates for team lead and members
                                email_type = "team_lead" if i == 0 else "team_member"
                                email_sent = send_confirmation_email(
                                    recipient_email=member["email"],
                                    recipient_name=member["name"],
                                    team_name=st.session_state.selectedTeam,
                                    submission_type="Team",
                                    team_details={
                                        "team_name": team_name.strip(),
                                        "member_count": len(valid_members),
                                        "team_lead_name": valid_members[0]["name"]
                                    },
                                    email_type=email_type
                                )
                                email_results.append(email_sent)
                            except Exception as e:
                                email_results.append(False)
                                st.error(f"Email error for {member['name']}: {str(e)}")
                        
                        st.session_state.form_submitted = True
                        st.session_state.submission_type = "team"
                        st.session_state.team_name = team_name.strip()
                        st.session_state.member_count = len(valid_members)
                        st.session_state.successful_emails = sum(email_results)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save team application. Please try again.")