import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Load from secrets instead of file
creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open sheet by ID
sheet_id = "15R_7NwIfIq66pWApCNtY3xhNR9OLA4UIP5KeKehIaQg"
sheet = client.open_by_key(sheet_id).sheet1

# --- Streamlit form ---
st.title("📋 Knowledge Sharing Circle - Member Recruitment Form")

with st.form("member_form"):
    name = st.text_input("Full Name")
    crn = st.text_input("CRN")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email")
    team = st.selectbox("Team", ["Content", "Tech", "Event", "Design"])
    submitted = st.form_submit_button("Submit")

    if submitted:
        if name and crn and contact and email:
            sheet.append_row([name, crn, contact, email, team])
            st.success("✅ Your response has been recorded!")
        else:
            st.error("⚠️ Please fill all fields before submitting.")

# --- Display existing responses (optional) ---
if st.checkbox("📄 Show all submissions"):
    data = sheet.get_all_records()
    st.write(data)
