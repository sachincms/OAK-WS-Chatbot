import streamlit as st

pages = [
    st.Page("chat_app.py", title = "Chatbot"),
    st.Page("manage_users.py", title = "User Management"),
]

pg = st.navigation(pages)
pg.run()