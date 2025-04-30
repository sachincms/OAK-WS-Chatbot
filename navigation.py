import streamlit as st

pages = [
    st.Page("chat_app.py", title = "Chatbot"),
    st.Page("case_stories.py", title = "Case Stories"),
    st.Page("manage_users.py", title = "User Management")
]

pg = st.navigation(pages)
pg.run()