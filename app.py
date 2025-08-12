import streamlit as st
import requests
from urllib.parse import urlencode
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets
import time

# Configuration
class Config:
    def __init__(self):
        # Load from environment variables or Streamlit secrets
        self.CLIENT_ID = self._get_secret('GOOGLE_CLIENT_ID', 'google_oauth', 'client_id')
        self.CLIENT_SECRET = self._get_secret('GOOGLE_CLIENT_SECRET', 'google_oauth', 'client_secret')
        
        # Validate that secrets are loaded
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            st.error("❌ Google OAuth credentials not found. Please check your environment variables or secrets configuration.")
            st.stop()
        
        # Determine redirect URI based on environment
        # Multiple methods to detect Streamlit Cloud deployment
        is_streamlit_cloud = (
            # Check for Streamlit Cloud environment variables
            os.getenv('STREAMLIT_SERVER_PORT') is not None or
            os.getenv('STREAMLIT_SHARING_URL') is not None or
            # Check if running on streamlit.app domain
            'streamlit.app' in str(os.getenv('STREAMLIT_SHARING_URL', '')) or
            # Check for other Streamlit Cloud indicators
            os.getenv('HOME', '').startswith('/home/appuser') or
            os.getenv('USER') == 'appuser' or
            # Check current working directory pattern
            '/app' in os.getcwd() or
            # Check if we can detect streamlit cloud from hostname
            any('streamlit' in str(val).lower() for val in os.environ.values())
        )
        
        if is_streamlit_cloud:
            self.REDIRECT_URI = 'https://ksc-khec.streamlit.app'
        else:
            self.REDIRECT_URI = 'http://localhost:8501/'
        
        self.SCOPES = ['openid', 'email', 'profile']
        self.GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
        self.GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    
    def _get_secret(self, env_var, secrets_section, secrets_key):
        """Get secret from environment variable or Streamlit secrets"""
        # First try environment variable
        value = os.getenv(env_var)
        if value:
            return value
        
        # Then try Streamlit secrets
        try:
            return st.secrets[secrets_section][secrets_key]
        except (KeyError, FileNotFoundError):
            return None

config = Config()

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'auth_time' not in st.session_state:
        st.session_state.auth_time = None

def generate_state():
    """Generate a random state parameter for CSRF protection"""
    return secrets.token_urlsafe(16)  # Shorter state for better compatibility

def get_google_auth_url():
    """Generate Google OAuth authorization URL"""
    # Generate new state and store it
    state = generate_state()
    st.session_state.oauth_state = state
    st.session_state.auth_time = time.time()
    
    params = {
        'client_id': config.CLIENT_ID,
        'redirect_uri': config.REDIRECT_URI,
        'scope': ' '.join(config.SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
        'include_granted_scopes': 'true'
    }
    
    return f"{config.GOOGLE_AUTH_URL}?{urlencode(params)}"

def is_state_valid(received_state):
    """Check if the received state is valid"""
    if not received_state or not st.session_state.oauth_state:
        return False
    
    # Check if state matches
    if received_state != st.session_state.oauth_state:
        return False
    
    # Check if state is not too old (10 minutes max)
    if st.session_state.auth_time:
        age = time.time() - st.session_state.auth_time
        if age > 600:  # 10 minutes
            return False
    
    return True

def exchange_code_for_token(authorization_code, state=None):
    """Exchange authorization code for access token"""
    # Skip state validation in development if needed
    is_development = 'localhost' in config.REDIRECT_URI
    
    if not is_development and state:
        if not is_state_valid(state):
            st.error("Authentication session expired or invalid. Please try again.")
            return None
    
    token_data = {
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': config.REDIRECT_URI,
    }
    
    try:
        response = requests.post(config.GOOGLE_TOKEN_URL, data=token_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error exchanging code for token: {str(e)}")
        return None

def get_user_info(access_token):
    """Get user information from Google API"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(config.GOOGLE_USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching user info: {str(e)}")
        return None

def logout():
    """Clear session state and logout user"""
    # Clear all authentication related session state
    keys_to_clear = ['authenticated', 'user_info', 'access_token', 'oauth_state', 'auth_time']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear URL parameters
    st.query_params.clear()
    st.rerun()

def display_user_profile(user_info):
    """Display user profile information"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_info.get('picture'):
            st.image(user_info['picture'], width=150, caption="Profile Picture")
        else:
            st.info("No profile picture available")
    
    with col2:
        st.subheader("Welcome!")
        st.write(f"**Name:** {user_info.get('name', 'N/A')}")
        st.write(f"**Email:** {user_info.get('email', 'N/A')}")
        st.write(f"**Google ID:** {user_info.get('id', 'N/A')}")
        
        if user_info.get('verified_email'):
            st.success("✅ Email Verified")
        else:
            st.warning("⚠️ Email Not Verified")
        
        # Additional user info if available
        if user_info.get('locale'):
            st.write(f"**Locale:** {user_info['locale']}")
        
        # Display authentication time
        if st.session_state.auth_time:
            auth_time = datetime.fromtimestamp(st.session_state.auth_time)
            st.write(f"**Authenticated at:** {auth_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Logout button
        st.markdown("---")
        col_logout1, col_logout2, col_logout3 = st.columns([1, 1, 1])
        with col_logout2:
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logout()

def handle_auth_callback():
    """Handle the OAuth callback"""
    query_params = st.query_params
    
    if 'code' in query_params and not st.session_state.authenticated:
        authorization_code = query_params.get('code')
        state = query_params.get('state')
        error = query_params.get('error')
        
        # Handle OAuth errors
        if error:
            st.error(f"OAuth Error: {error}")
            if error == 'access_denied':
                st.info("You denied access to the application. Please try again if you want to proceed.")
            return False
        
        if authorization_code:
            with st.spinner("🔐 Authenticating with Google..."):
                # Exchange code for token
                token_response = exchange_code_for_token(authorization_code, state)
                
                if token_response and 'access_token' in token_response:
                    access_token = token_response['access_token']
                    
                    # Get user information
                    user_info = get_user_info(access_token)
                    
                    if user_info:
                        # Store in session state
                        st.session_state.user_info = user_info
                        st.session_state.access_token = access_token
                        st.session_state.authenticated = True
                        
                        # Clear URL parameters
                        st.query_params.clear()
                        st.success("✅ Authentication successful!")
                        st.rerun()
                        return True
                    else:
                        st.error("❌ Failed to retrieve user information from Google.")
                else:
                    st.error("❌ Failed to get access token from Google.")
                
                # Clear state on failure
                st.session_state.oauth_state = None
                st.session_state.auth_time = None
    
    return False

def show_login_page():
    """Display the login page"""
    # Debug information
    st.info(f"🔍 Debug - Redirect URL: {config.REDIRECT_URI}")
    st.info(f"🔍 Debug - Current Working Dir: {os.getcwd()}")
    st.info(f"🔍 Debug - User: {os.getenv('USER', 'Not found')}")
    st.info(f"🔍 Debug - Home: {os.getenv('HOME', 'Not found')}")
    st.info(f"🔍 Debug - Streamlit Server Port: {os.getenv('STREAMLIT_SERVER_PORT', 'Not found')}")
    st.info(f"🔍 Debug - Environment Keys with 'streamlit': {st.secrets}")
    
    st.info("👋 Please sign in with your Google account to continue.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if we're in the middle of an auth flow
        query_params = st.query_params
        if 'error' in query_params:
            error = query_params.get('error')
            if error == 'access_denied':
                st.warning("⚠️ You need to grant permission to continue.")
            else:
                st.error(f"Authentication error: {error}")
        
        auth_url = get_google_auth_url()
        
        # Debug: Show the auth URL
        st.code(f"Auth URL: {auth_url}")
        
        # Custom Google Sign-in button
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <a href="{auth_url}" target="_self" style="text-decoration: none;">
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        background-color: #4285f4;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 500;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: background-color 0.2s;
                        gap: 12px;
                    " onmouseover="this.style.backgroundColor='#3367d6'" 
                       onmouseout="this.style.backgroundColor='#4285f4'">
                        <svg width="20" height="20" viewBox="0 0 24 24" style="flex-shrink: 0;">
                            <path fill="white" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="white" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="white" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="white" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        <span>Sign in with Google</span>
                    </div>
                </a>
            </div>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Google OAuth Demo",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🔐 Google OAuth Authentication Demo")
    st.markdown("---")
    
    # Handle OAuth callback first
    if not st.session_state.authenticated:
        handle_auth_callback()
    
    # Main app logic
    if st.session_state.authenticated and st.session_state.user_info:
        # User is authenticated - show profile
        display_user_profile(st.session_state.user_info)
        
        # Additional features section
        st.markdown("---")
        st.subheader("📊 Session Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Authentication Status", "✅ Active")
        
        with col2:
            if st.session_state.auth_time:
                duration = int(time.time() - st.session_state.auth_time)
                minutes = duration // 60
                seconds = duration % 60
                st.metric("Session Duration", f"{minutes}m {seconds}s")
        
        with col3:
            if st.button("🔄 Refresh Profile", help="Refresh your profile information"):
                if st.session_state.access_token:
                    with st.spinner("Refreshing..."):
                        user_info = get_user_info(st.session_state.access_token)
                        if user_info:
                            st.session_state.user_info = user_info
                            st.success("Profile refreshed successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to refresh profile. Please login again.")
        
        # Debug information (for development)
        if st.checkbox("🐛 Show Debug Info", help="Toggle to show technical details"):
            st.subheader("🔧 Debug Information")
            debug_info = {
                "redirect_uri": config.REDIRECT_URI,
                "client_id": config.CLIENT_ID[:20] + "...",
                "scopes": config.SCOPES,
                "user_id": st.session_state.user_info.get('id'),
                "email_verified": st.session_state.user_info.get('verified_email'),
                "auth_timestamp": st.session_state.auth_time,
                "session_keys": list(st.session_state.keys())
            }
            st.json(debug_info)
    
    else:
        # User is not authenticated - show login
        show_login_page()

if __name__ == "__main__":
    main()