import streamlit as st
from utils.auth_db import get_user_role, get_all_users, approve_user, promote_user_to_admin, delete_user
from time import sleep
from config import LOGOUT_BUTTON_STYLE

st.set_page_config(page_title = "manage users", layout = "wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please log in to view this page.")
    st.stop()

if get_user_role(st.session_state["username"]) != "admin":
    st.error("Access denied. Admins only.")
    st.stop()


st.title("User Management")

with open(LOGOUT_BUTTON_STYLE) as f:
        st.markdown(f.read(), unsafe_allow_html=True)
    
if st.button("Logout", type="primary"):
    st.session_state["authenticated"] = False
    st.rerun()

users_df = get_all_users()

if not users_df.empty:
    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2], border=True)
    col1.markdown("**👤 Username**")
    col2.markdown("**📋 Role**")
    col3.markdown("**📌 Status**")
    col4.markdown("**✅ Approve**")
    col5.markdown("**👑 Make Admin**")
    col6.markdown("**❌ Delete**")

    for index, row in users_df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 2], border=True)
        user_id = row["_id"]

        with col1:
            st.write(f"{row["username"]}")
        with col2:
            st.write(f"{row["role"]}")
        with col3:
            st.write(f"{row["status"]}")

        if row["status"] == "pending":
            if col4.button("Approve", key = f"approve_{user_id}"):
                if approve_user(user_id):
                    st.success(f"Approved {row["username"]}.")
                else:
                    st.error(f"Error approving {row['username']}. Please try again.")

                sleep(5)
                st.rerun()
        else:
            col4.write("-")

        if row["role"] == "user":
            if col5.button("Make Admin", key=f"admin_{user_id}"):
                promote_user_to_admin(user_id)
                st.success(f"👑 Promoted: {row['username']}")
                sleep(2)
                st.rerun()
        else:
            col5.write("—")

        if row["username"] != st.session_state["username"]:
            if col6.button("Delete", key=f"delete_{user_id}"):
                delete_user(user_id)
                st.warning(f"❌ Deleted: {row['username']}")
                sleep(2)
                st.rerun()
        else:
            col6.write("—")
else:
    st.write("No users")

