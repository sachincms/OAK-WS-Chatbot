import streamlit as st


pages = [
    st.Page("chat_app.py", title = "SPF chatbot"),
    st.Page("manage_users.py", title = "manage users")
]




pg = st.navigation(pages)
pg.run()