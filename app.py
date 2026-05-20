import streamlit as st
import sys
from streamlit.web import cli as stcli

# Automatically launch Streamlit if run directly with standard Python interpreter
if __name__ == '__main__':
    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

import time
import database
import auth
import styles
import admin
import student

# 1. Establish Page Configurations
st.set_page_config(
    page_title="EduTest | Online Examination System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Global Premium CSS
styles.inject_custom_css()

# 3. Initialize Global Session States
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'full_name' not in st.session_state:
    st.session_state.full_name = None

# ----------------- Main View Router -----------------

def render_login_register():
    """Render a premium glassmorphic Authentication Landing Page."""
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><span class="gradient-text">🎓 EduTest Portal</span><p style="color: #a0aec0; font-size: 1.1rem; margin-top: 5px;">Advanced Examination & MCQ Testing Hub</p></div>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    
    with col_l2:
        auth_mode = st.radio(
            "Authentication Mode",
            ["Student/Admin Login", "New Student Registration"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        if auth_mode == "Student/Admin Login":
            st.markdown('<h3 style="text-align: center; margin-bottom: 20px; color:#ffffff;">🔒 Sign In</h3>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username / ID", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit_login = st.form_submit_button("Authenticate Securely", use_container_width=True)
                
                if submit_login:
                    success, msg = auth.login_user(username, password)
                    if success:
                        st.success(msg)
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error(msg)
                        
            # Helpful hints for testing
            st.markdown("""
            <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; text-align: center;">
                🔑 <b>Default Testing Accounts:</b><br/>
                Student: <code>student</code> / <code>student123</code><br/>
                Admin: <code>admin</code> / <code>admin123</code>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown('<h3 style="text-align: center; margin-bottom: 20px; color:#ffffff;">👤 Student Sign Up</h3>', unsafe_allow_html=True)
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
                username = st.text_input("Create Username", placeholder="e.g. janedoe12")
                password = st.text_input("Choose Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Retype password")
                submit_register = st.form_submit_button("Complete Student Registration", use_container_width=True)
                
                if submit_register:
                    success, msg = auth.register_user(username, password, confirm_password, full_name, role='student')
                    if success:
                        st.success(msg)
                        st.info("Registration complete! You can now switch to the Login tab to sign in.")
                    else:
                        st.error(msg)
                        
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard_workspace():
    """Render the responsive sidebar navigation and route appropriate dashboards."""
    # Sidebar Profile Card
    st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px; padding: 15px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px;">
        <div style="font-size: 2.5rem; margin-bottom: 5px;">👤</div>
        <div style="font-weight: 700; color: #ffffff; font-size:1.1rem;">{st.session_state.full_name}</div>
        <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 8px;">@{st.session_state.username}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Elegant custom badge in sidebar for Role
    role_color = "#FF8E53" if st.session_state.role == 'admin' else "#4D96FF"
    st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: 25px;">
        <span class="custom-badge" style="background-color: {role_color}15; color: {role_color}; border: 1px solid {role_color}40; padding: 4px 14px; font-size: 0.8rem;">
            🛡️ {st.session_state.role.upper()} PORTAL
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar utility buttons (hide if student is currently mid-exam to prevent exit)
    is_mid_exam = st.session_state.get('active_exam_id', None) is not None
    
    if not is_mid_exam:
        st.sidebar.markdown("---")
        if st.sidebar.button("🔓 Secure Sign Out", use_container_width=True, type="secondary"):
            auth.logout_user()
    else:
        st.sidebar.markdown("""
        <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 8px; padding: 10px; text-align: center; font-size: 0.8rem; color: #FF6B6B;">
            🔒 <b>Navigation Locked</b><br/>
            Finish or submit your active examination to log out or leave the portal.
        </div>
        """, unsafe_allow_html=True)

    # Route Workspace Based on Authenticated Role
    if st.session_state.role == 'admin':
        admin.show_admin_dashboard()
    elif st.session_state.role == 'student':
        student.show_student_dashboard()
    else:
        auth.logout_user()

# Primary Routing Engine
if not st.session_state.logged_in:
    render_login_register()
else:
    render_dashboard_workspace()
