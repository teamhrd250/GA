import streamlit as st

USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user456"
}

def login():
    st.title("🔐 Asset Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Selamat datang, {username}!")
            st.switch_page("pages/main.py")
        else:
            st.error("Username atau password salah.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if st.session_state.logged_in:
    st.switch_page("pages/main.py")
else:
    login()