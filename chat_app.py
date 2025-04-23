from config import SPF_LOGO_PATH, SWASTI_LOGO_PATH, DEFAULT_QUERY, DEFAULT_FINAL_RESPONSE, ERROR_MESSAGE, PHASE1_JSON_FILE_PATH, PHASE2_WITH_SDD_JSON_FILE_PATH, ALL_PHASES_JSON_FILE_PATH
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.chat import qa_chat_with_prompt, stream_data
from utils.image_processing import display_images
from utils.files_processing import convert_excel_to_dict
from utils.auth_db import init_db, authenticate_user, add_user, get_user_role, get_all_users, approve_user, promote_user_to_admin, delete_user
import warnings
warnings.simplefilter("ignore", ResourceWarning)
import asyncio
import logging
import uuid
from streamlit.web.server.websocket_headers import _get_websocket_headers
from traceloop.sdk import Traceloop
from time import sleep
import json
from logging_config import get_logger
import os

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
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type = "password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("Login successful")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
            else:
                st.error("Invalid credentials")

    with register_tab:
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type = "password")
        if st.button("Register"):
            if add_user(new_username, new_password):
                st.success("User registered....")
            else:
                st.error("Username already exists or error occured")




# st.write(INTRO_MESSAGE)
# st.markdown(INTRO_MARKDOWN, unsafe_allow_html=True)

if st.session_state["authenticated"]:
    st.write(f"Welcome {st.session_state["username"]}")


    context_options = {
        "All Phases": ALL_PHASES_JSON_FILE_PATH,
        "Phase 1": PHASE1_JSON_FILE_PATH,
        "Phase 2": PHASE2_WITH_SDD_JSON_FILE_PATH,
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


if st.button("Logout"):
    st.session_state["authenticated"]= False
    st.rerun()
