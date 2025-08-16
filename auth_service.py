import streamlit as st
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests

def initialize_auth():
    # Initialize session state for credentials
    if "credentials" not in st.session_state:
        st.session_state.credentials = None

    # Config
    CLIENT_ID = st.secrets["gcp_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["gcp_oauth"]["client_secret"]
    REDIRECT_URI = st.secrets["gcp_oauth"]["redirect_uri"]

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]

    if not st.session_state.credentials:
        # st.write("## 🔑 Login with Google")

        # Construct Flow
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

        # Get code as string
        code = st.query_params.get("code")
        if code:
            try:
                flow.fetch_token(code=code)
                st.session_state.credentials = flow.credentials
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
                st.query_params.clear()
                st.rerun()

def get_user_info():
    if st.session_state.credentials:
        creds = st.session_state.credentials
        request_session = requests.Session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        if creds.expired and creds.refresh_token:
            creds.refresh(token_request)

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {creds.token}"}
        ).json()

        return {
            "name": user_info.get("name", ""),
            "email": user_info.get("email", ""),
            "picture": user_info.get("picture", "")
        }
    return None