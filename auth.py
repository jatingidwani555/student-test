import streamlit as st
import database

def login_user(username, password):
    """Authenticate user credentials and initialize session states."""
    username = username.strip()
    if not username or not password:
        return False, "Please enter both username and password."
        
    user = database.get_user(username)
    if not user:
        return False, "Invalid username or password."
        
    # Hash password with retrieved salt
    retrieved_hash = user['password_hash']
    salt = user['salt']
    
    computed_hash, _ = database.hash_password(password, salt)
    
    if computed_hash == retrieved_hash:
        st.session_state.logged_in = True
        st.session_state.username = user['username']
        st.session_state.role = user['role']
        st.session_state.full_name = user['full_name']
        return True, "Login successful!"
    else:
        return False, "Invalid username or password."

def register_user(username, password, confirm_password, full_name, role='student'):
    """Register a new user after validation and password hashing."""
    username = username.strip().lower()
    full_name = full_name.strip()
    
    if not username:
        return False, "Username is required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if password != confirm_password:
        return False, "Passwords do not match."
    if not full_name:
        return False, "Full Name is required."
        
    # Check if user already exists
    existing = database.get_user(username)
    if existing:
        return False, "Username is already taken."
        
    # Securely hash password and save
    hashed, salt = database.hash_password(password)
    success, msg = database.create_user(username, hashed, salt, role, full_name)
    return success, msg

def logout_user():
    """Clear user session states and trigger page refresh."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None
    if 'exam_state' in st.session_state:
        del st.session_state.exam_state
    st.rerun()
