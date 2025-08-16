import streamlit as st

def add_custom_css():
    """Add custom CSS for better mobile experience and clean styling"""
    st.write("""
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
    
    /* Team Lead styling */
    .team-lead-badge {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
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
    st.write("""
    <div class="main-container">
        <div class="main-header">
            <div class="main-title">🌟 Knowledge Sharing Circle</div>
            <div class="main-subtitle">Join Our Community • Share Knowledge • Grow Together</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_executive_modal():
    """Display executive members modal with an image using Streamlit components"""
    if st.session_state.show_exec_modal:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col3:
                if st.button("✖️ Close", key="close_exec_modal", use_container_width=True):
                    st.session_state.show_exec_modal = False
                    st.rerun()
            
            st.write("<h3>👥 Meet Our Executive Team</h3>", unsafe_allow_html=True)
            st.write("<hr>", unsafe_allow_html=True)
            
            try:
                st.image("assets/executives.png", use_column_width=True)
            except FileNotFoundError:
                st.error("⚠️ Image file 'assets/executives.png' not found. Please ensure the file exists.")
            except Exception as e:
                st.error(f"⚠️ Error loading image: {str(e)}")

def display_exec_toggle_button():
    """Display centered button to show executive info"""
    if not st.session_state.show_exec_modal:
        st.write('<div class="center-btn-container">', unsafe_allow_html=True)
        if st.button("👥 View Executive Members", key="show_exec_btn", help="View the info about Executive Members", use_container_width=True):
            st.session_state.show_exec_modal = True
            st.rerun()
        st.write('</div>', unsafe_allow_html=True)

def display_team_guidelines():
    """Display team guidelines using Streamlit components"""
    if st.session_state.selectedTeam:
        team_info = st.session_state.data.get(st.session_state.selectedTeam, {})
        
        with st.container():
            st.write(f"<h3>📋 {st.session_state.selectedTeam}</h3>", unsafe_allow_html=True)
            
            with st.expander("✨ Why Join?", expanded=True):
                st.write(team_info.get("Why Join", ""))
            
            with st.expander("🎯 Key Responsibilities", expanded=True):
                for responsibility in team_info.get("Key Responsibilities", []):
                    st.write(f"• {responsibility}")
            
            with st.expander("⚠️ Why Avoid?", expanded=True):
                st.write(team_info.get("Why Avoid", ""))
    else:
        with st.container():
            st.write("<h3>🌟 Knowledge Sharing Circle</h3>", unsafe_allow_html=True)
            
            with st.expander("📖 About Us", expanded=True):
                st.write(st.session_state.circle_data.get("circle_info", {}).get("about", ""))
            
            with st.expander("🎯 Our Mission", expanded=True):
                for mission_item in st.session_state.circle_data.get("circle_info", {}).get("mission", []):
                    st.write(f"• {mission_item}")
            
            with st.expander("🔮 Vision", expanded=True):
                st.write(st.session_state.circle_data.get("circle_info", {}).get("vision", ""))