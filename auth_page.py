import streamlit as st
import firebase_admin
from firebase_admin import auth
import firebase_config

# Function to check if the email is from the qubit.capital domain
def is_qubit_email(email):
    return email.endswith('@qubit.capital')

# Function to handle user registration
def register_user(email, password):
    if not is_qubit_email(email):
        st.error("Only emails with the domain @qubit.capital are allowed.")
        return None
    
    try:
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        st.success("User registered successfully. Please log in.")
        return user
    except firebase_admin.exceptions.FirebaseError as e:
        st.error(f"Error: {e}")
        return None

# Function to handle user login
def login_user(email, password):
    if not is_qubit_email(email):
        st.error("Only emails with the domain @qubit.capital are allowed.")
        return None
    
    try:
        user = auth.get_user_by_email(email)
        st.success(f"Welcome back, {user.email}!")
        st.session_state.user_authenticated = True
        st.session_state.user_email = email
        
        # Simulate a page reload by setting query parameters
        st.experimental_set_query_params(logged_in="true")
        
        return user
    except firebase_admin.exceptions.FirebaseError as e:
        error_code = e.detail.get('error', {}).get('message', '')
        st.error(f"Firebase Error: {error_code}")
        return None

# Streamlit app for user login/registration
def auth_page():
    st.title("Login/Register")

    choice = st.selectbox("Login or Register", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            register_user(email, password)
    
    if choice == "Login":
        if st.button("Login"):
            login_user(email, password)
