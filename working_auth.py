import streamlit as st
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests

# -----------------------
# CONFIG
# -----------------------
CLIENT_ID = st.secrets["gcp_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["gcp_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["gcp_oauth"]["redirect_uri"]

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

st.set_page_config(page_title="Google Login Demo", page_icon="🔑")

# -----------------------
# SESSION STATE
# -----------------------
if "credentials" not in st.session_state:
    st.session_state.credentials = None

# -----------------------
# LOGIN FLOW
# -----------------------
if not st.session_state.credentials:
    st.write("## 🔑 Login with Google")

    # Construct Flow using client_id and client_secret
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f"[Click here to Login with Google]({auth_url})")

    # Fixed: Get code as string, not list
    code = st.query_params.get("code")
    if code:
        try:
            # Use code directly, not code[0]
            flow.fetch_token(code=code)
            st.session_state.credentials = flow.credentials

            # Clear the code param to prevent loop
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
            # Clear params to allow retry
            st.query_params.clear()
            st.rerun()

# -----------------------
# SHOW USER INFO
# -----------------------
else:
    creds = st.session_state.credentials
    request_session = requests.Session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(token_request)

    # Fetch user info from Google API
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {creds.token}"}
    ).json()

    st.success("✅ Logged in successfully!")
    st.write("### 👤 Your Google Profile Info")
    st.write(f"**Name:** {user_info.get('name')}")
    st.write(f"**Email:** {user_info.get('email')}")
    st.image(user_info.get("picture", ""), width=100)

    if st.button("Logout"):
        st.session_state.credentials = None
        st.query_params.clear()
        st.rerun()