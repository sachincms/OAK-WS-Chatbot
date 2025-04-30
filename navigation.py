import streamlit as st
import os

pages = [
    st.Page(os.path.join("app_pages", "chatbot.py"), title = "Chatbot"),
    st.Page(os.path.join("app_pages", "case_stories.py"), title = "Case Stories"),
    st.Page(os.path.join("app_pages", "user_management.py"), title = "User Management")
]

pg = st.navigation(pages)
pg.run()