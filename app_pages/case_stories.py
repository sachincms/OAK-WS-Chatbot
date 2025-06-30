import streamlit as st
import time
from markdown_pdf import MarkdownPdf
import os
from utils.case_story_generation import generate_case_story, check_case_story_exists, store_case_story, get_case_story_pdf
from utils.files_processing import load_dict_from_json
from utils.app_components import display_logout_button
from utils.chat import stream_data, qa_chat_with_prompt
from config import OUTCOME_JOURNALS_PATH, OUTCOME_JOURNALS_DICT, PROGRESS_REPORT_PARTNERS_PATH, PROGRESS_REPORT_PARTNERS_DICT, SPF_LOGO_PATH, ERROR_MESSAGE, OUTCOME_JOURNALS_DOCUMENT_TYPE, PROGRESS_DOCUMENT_TYPE
from logging_config import get_logger


logger = get_logger(__name__)


st.set_page_config(
    page_title="Case Stories",
    page_icon=SPF_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please log in to view this page.")
    st.stop()

if "case_story_chat_history" not in st.session_state:
    st.session_state["case_story_chat_history"] = []

if "initial_case_story_rendered" not in st.session_state:
    st.session_state["initial_case_story_rendered"] = False

if "last_case_story_rendered" not in st.session_state:
    st.session_state["last_case_story_rendered"] = None


display_logout_button()
st.title("Case Stories")


main_document = st.radio("Select main document", [OUTCOME_JOURNALS_DOCUMENT_TYPE, PROGRESS_DOCUMENT_TYPE])


def export_case_story(pdf_file: MarkdownPdf, pdf_name: str) -> None:

    pdf_file.save(f'{pdf_name}_case_story.pdf')

    with open(f'{pdf_name}_case_story.pdf', "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    st.download_button(
        label="Export Case Story",
        data=pdf_bytes,
        file_name=pdf_name,
    )

    os.remove(f'{pdf_name}_case_story.pdf')


def get_case_story_identifier(identifier_params: dict) -> str:
    case_story_identifier = str(list(identifier_params.values()))
    return case_story_identifier


def generate_and_display_case_story(document_type: str, identifier_params: dict, text: str, display_name: str) -> None:
    existing_case_story = check_case_story_exists(document_type=document_type, **identifier_params)
    
    if existing_case_story:
        case_story = existing_case_story["case_story"]
        with st.spinner(f"Generating case story for {display_name}..."):
            time.sleep(2)
    else:
        with st.spinner(f"Generating case story for {display_name}..."):
            case_story = generate_case_story(text=text)
            if case_story:
                store_case_story(case_story=case_story, document_type=document_type, **identifier_params)
    
    if case_story and not st.session_state["initial_case_story_rendered"]:
        st.write_stream(stream_data(case_story))
        st.session_state["case_story_chat_history"].append({
            "role": "assistant",
            "message": case_story,
            "rerender": "no"
        })
        st.session_state["initial_case_story_rendered"] = True
        
        case_story_identifier = get_case_story_identifier(identifier_params)
        st.session_state["last_case_story_rendered"] = case_story_identifier
    
    else:
        st.write(case_story)

    if case_story:
        export_case_story(
            pdf_file=get_case_story_pdf(case_story_markdown=case_story),
            pdf_name=f"{display_name}_case_story.pdf"
        )





if main_document == OUTCOME_JOURNALS_DOCUMENT_TYPE:

    json_data = load_dict_from_json(OUTCOME_JOURNALS_PATH)

    select_journal = st.selectbox("Select Journal", options = OUTCOME_JOURNALS_DICT.keys())
    if select_journal:
        journal = OUTCOME_JOURNALS_DICT[select_journal]
        select_partner = st.selectbox("Select Partner", options = json_data[journal].keys(), index=None)
        

        if select_partner:
            identifier_params={
                "journal_name": journal,
                "partner_name": select_partner
            }

            case_story_identifier = get_case_story_identifier(identifier_params)

            if case_story_identifier != st.session_state["last_case_story_rendered"]:
                st.session_state["case_story_chat_history"] = []
                st.session_state["initial_case_story_rendered"] = False

            text = json_data[journal][select_partner]

            generate_and_display_case_story(
                document_type=OUTCOME_JOURNALS_DOCUMENT_TYPE,
                identifier_params=identifier_params,
                text=text,
                display_name=select_partner
            )



else:

    json_data = load_dict_from_json(PROGRESS_REPORT_PARTNERS_PATH)

    select_pdf = st.selectbox("Select PDF", options = PROGRESS_REPORT_PARTNERS_DICT.keys(), index = None)
    if select_pdf:
        identifier_params={
            "pdf_name": select_pdf
        }

        case_story_identifier = get_case_story_identifier(identifier_params)
        if case_story_identifier != st.session_state["last_case_story_rendered"]:
            st.session_state["case_story_chat_history"] = []
            st.session_state["initial_case_story_rendered"] = False

        pdf = PROGRESS_REPORT_PARTNERS_DICT[select_pdf]
        existing_case_story = check_case_story_exists(
                document_type = PROGRESS_DOCUMENT_TYPE,
                pdf_name = pdf,
            )
        
        text = json_data[pdf]

        generate_and_display_case_story(
            document_type=PROGRESS_DOCUMENT_TYPE,
            identifier_params=identifier_params,
            text=text,
            display_name=select_pdf
        )

            
 

if query:= st.chat_input("Ask a question about the case stories."):
    st.session_state["case_story_chat_history"].append({
        "role": "user",
        "message": query,
        "rerender": "yes"
    })

    for chat in st.session_state["case_story_chat_history"]:
        if "rerender" in chat and chat["rerender"] == "yes":
            with st.chat_message(chat["role"]):
                st.write(chat["message"])

    if st.session_state["case_story_chat_history"][-1]["role"] != "assistant":
        try:
            def build_chat_context(chat_history: list, context: str):
                context_parts = [f"""
                    The following is the initial prompt and context based on which the first case story was generated by you:
                    --------------- Start of Instructions ---------------
                    You are a development impact writer. Based on the context below, generate a NEW case story.
                    Use a compelling, human-centered tone. Structure it with:
                    1. Title (Should capture the transformation)

                    2. Context (2-3 lines)
                    Geographic + thematic background
                    Why this story matters

                    3. The Problem
                    What issue was being faced?
                    Who was most affected?

                    4. The Intervention
                    What did the partner do?
                    Who was involved (community, gov, other actors)?
                    Mention any tools, processes (like participatory planning, legal training, MIS systems, etc.)

                    5. Voices from the Ground (Optional)
                    A quote or story from a beneficiary or frontline worker (Only if there is a quote in the provided context. If not, skip this.)

                    6. Outcomes / Change Observed
                    Tangible results — behavioural change, system-level changes, impact numbers if any

                    7. What’s Next / Sustainability
                    Is the change embedded?
                    What are the next steps or replication ideas?
                    --------------- End of Instructions ---------------
                                 
                    --------------- Start of Context ---------------
                    {context}
                    --------------- End of Context ---------------


                    The following is a conversation between you and a user regarding generating a case story based on the above context. 
                    Any query the user asks you is with reference to the case story or the context.
                    Use the previous interactions of this user regarding this case story as context if required. 
                    If the user asks you to generate a new case story or modify the provided case story, you should follow the template provided in the instructions. 
                    Only if the user asks you to modify the structure of the case story, you're allowed to modify it. 
                    Do not use any information for the case story that is not provided in the context. 
                    Your responses are marked as 'assistant' and the users's queries are marked as 'user':
                """]
                
                for chat_item in chat_history:
                    role = chat_item["role"]
                    message = chat_item["message"]
                    context_parts.append(f"{role}: {message}")
                
                return "\n".join(context_parts)

            query = build_chat_context(chat_history=st.session_state["case_story_chat_history"], context=text) + "\nHere is the new query:\n" + query
            
            response = qa_chat_with_prompt(text=text, query=query, chat_history=st.session_state["case_story_chat_history"])
            answer = response["answer"].strip("```").strip("json").strip('"answer": ')
            answer = answer.strip("{}").strip()


            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    st.write_stream(stream_data(answer))
                    st.session_state["case_story_chat_history"].append({
                        "role": "assistant",
                        "message": answer,
                        "rerender": "yes"
                    })

        except Exception as ex:
            logger.error(ex)
            st.session_state["case_story_chat_history"].append({
                "role": "assistant",
                "message": ERROR_MESSAGE
            })
            st.chat_message("assistant").write_stream(stream_data(ERROR_MESSAGE))
