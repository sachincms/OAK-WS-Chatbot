from config import SPF_LOGO_PATH, SWASTI_LOGO_PATH, DEFAULT_QUERY, DEFAULT_FINAL_RESPONSE, ERROR_MESSAGE, PHASE1_JSON_FILE_PATH, PHASE2_WITH_SDD_JSON_FILE_PATH, ALL_PHASES_JSON_FILE_PATH
import streamlit as st
import sys
import os
import warnings
warnings.simplefilter("ignore", ResourceWarning)
import asyncio
import logging
import uuid
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
from traceloop.sdk import Traceloop
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.chat import qa_chat_with_prompt, stream_data
from utils.image_processing import display_images
from utils.auth_db import init_db, authenticate_user, add_user
from config import LOGOUT_BUTTON_STYLE, AUTH_CONTAINER_STYLE, PROGRESS_REPORT_PARTNERS_PATH, GAF_PATH
from logging_config import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="SPF chatbot",
    page_icon=SPF_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed",
)


display_images(SWASTI_LOGO_PATH, SPF_LOGO_PATH)

init_db()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


if not st.session_state["authenticated"]:
    if "login_method" not in st.session_state:
        st.session_state["login_method"] = "login"

    with open(AUTH_CONTAINER_STYLE) as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    _, col2, _ = st.columns([2, 3, 2])

    if st.session_state["login_method"] == "login":
        with col2:
            with st.container(border=True):
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type = "password")
                
                button_container_1 = st.container()
                create_col, _, login_col = button_container_1.columns([3, 1, 1])

                with create_col:
                    if st.button("Create Account"):
                        st.session_state["login_method"] = "register"
                        st.rerun()

                with login_col:

                    if st.button("Login", type="primary"):
                        if authenticate_user(username, password):
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.success("Login successful")
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                
    
    if st.session_state["login_method"] == "register":
        with col2:
            with st.container(border=True):
                st.subheader("Register")
                full_name = st.text_input("Full Name")
                new_username = st.text_input("New Username")
                email = st.text_input("Email")
                new_password = st.text_input("New Password", type = "password")
                reenter_password = st.text_input("Re-enter Password", type = "password")
                
                user_data = {
                    "full_name": full_name,
                    "username": new_username,
                    "email": email,
                    "password": new_password,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                button_container_2 = st.container()
                register_col, back_col = button_container_2.columns(2)

                registration_successful = None
                with register_col:
                    if st.button("Register"):
                        if new_password != reenter_password:
                            st.error("Passwords do not match.")

                        elif add_user(user_data):
                            registration_successful = True
                            
                        else:
                            registration_successful = False
                    
                if registration_successful:
                    st.success("User registered. Please wait for admin approval.")
                elif registration_successful == False:
                    st.error("Please enter valid details using the following guidelines:\n1. Username must be between 3-20 characters and can only contain alphanumeric characters and underscores.\n2. Passwords must be at least 8 characters long and must contain at least one lowercase letter, one uppercase letter and one digit.\n3. Email address must be in a valid format.") 

                with back_col:
                    if st.button("Already have an account? Login."):
                        st.session_state["login_method"] = "login"
                        st.rerun()



if st.session_state["authenticated"]:
    st.subheader(f"Welcome {st.session_state["username"]}!")

    with open(LOGOUT_BUTTON_STYLE) as f:
        st.markdown(f.read(), unsafe_allow_html=True)
    
    if st.button("Logout", type="primary"):
        st.session_state["authenticated"] = False
        st.rerun()


    context_options = {
        "All Phases": ALL_PHASES_JSON_FILE_PATH,
        "Phase 1": PHASE1_JSON_FILE_PATH,
        "Phase 2": PHASE2_WITH_SDD_JSON_FILE_PATH,
        "Progress Report Partners": PROGRESS_REPORT_PARTNERS_PATH,
        "Grant Application Form": GAF_PATH
    }

    _, col2, _ = st.columns(3)

    with col2:
        context = st.selectbox(
            "Select Phase: ",
            context_options,
        )

    if "previous_context" not in st.session_state:
        st.session_state["previous_context"] = context

    if st.session_state["previous_context"] != context:

        st.session_state["chat_history"] = [
            {"role": "user", "message": DEFAULT_QUERY},
            {"role": "assistant", "message": DEFAULT_FINAL_RESPONSE},
        ]

        st.info(f"Changed context from {st.session_state["previous_context"]} to {context}.")

        st.session_state["previous_context"] = context
        
        file = context_options[context]
        text = json.load(open(file, "r", encoding="utf-8"))
        st.session_state["oak_data"] = text

    try:
        loop = asyncio.get_running_loop()
        loop.close()
    except RuntimeError:
        pass



    file = context_options[context]
    text = json.load(open(file, "r", encoding="utf-8"))
    st.session_state["oak_data"] = text

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []



    if "chat_container" not in st.session_state:
        st.session_state.chat_container = st.container()

    if "messages" not in st.session_state.keys():
        if "session_id" not in st.session_state.keys():
            session_id = "uuid-" + str(uuid.uuid4())

            logging.info(json.dumps({"_type": "set_session_id", "session_id": session_id}))
            Traceloop.set_association_properties({"session_id": session_id})
            st.session_state["session_id"] = session_id

            st.session_state["chat_history"] = [
                {"role": "user", "message": DEFAULT_QUERY},
                {"role": "assistant", "message": DEFAULT_FINAL_RESPONSE},
            ]

        #TODO: _get_websocket_headers is deprecated. Replace it with st.context.headers but even this is not JSON serializable so find a solution.
        # headers = _get_websocket_headers()
        # logging.info(
        #     json.dumps(
        #         {
        #             "_type": "set_headers",
        #             "headers": headers,
        #             "session_id": st.session_state.get("session_id", "NULL_SESS"),
        #         }
        #     )
        # )

    if query:= st.chat_input("Ask a question"):
        st.session_state["chat_history"].append({
            "role": "user", 
            "message": query, 
        })

    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.write(chat["message"])

    if st.session_state["chat_history"][-1]["role"] != "assistant":  
        try:
            response = qa_chat_with_prompt(text = text, query = query)
            answer = response["answer"]
            source = response["source"]
            full_response = f"\n{answer}\n\n**Source:** {source}"
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    st.write_stream(stream_data(full_response))
                    st.session_state["chat_history"].append({
                        "role": "assistant", 
                        "message": full_response, 
                    })
            
        except Exception as e:
            logging.error(e)
            st.session_state["chat_history"].append({
                "role": "assistant",
                "message": ERROR_MESSAGE,
            })
            st.chat_message("assistant").write_stream(stream_data(ERROR_MESSAGE))