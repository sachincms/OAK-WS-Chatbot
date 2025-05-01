import streamlit as st
from config import LOGOUT_BUTTON_STYLE


def display_logout_button():
    with open(LOGOUT_BUTTON_STYLE) as f:
        st.markdown(f.read(), unsafe_allow_html=True)
        
    if st.button("Logout", type="primary"):
        st.session_state["authenticated"] = False
        st.rerun()
