import streamlit as st
import time
from utils.generate_case_story import summarize_helper
from utils.files_processing import load_dict_from_json
from utils.case_story_db import check_case_story_exists, store_case_story
from utils.app_components import display_logout_button
from utils.chat import stream_data
from config import OUTCOME_JOURNALS_PATH, OUTCOME_JOURNALS_DICT, PROGRESS_REPORT_PARTNERS_PATH, PROGRESS_REPORT_PARTNERS_DICT, SPF_LOGO_PATH

st.set_page_config(
    page_title="Case Stories",
    page_icon=SPF_LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please log in to view this page.")
    st.stop()

display_logout_button()
st.title("Case Stories")

main_document = st.radio("Select main document", ["Outcome Journals", "Progess Report Partners"])

if main_document == "Outcome Journals":
    json_data = load_dict_from_json(OUTCOME_JOURNALS_PATH)

    select_journal = st.selectbox("Select Journal", options = OUTCOME_JOURNALS_DICT.keys())
    if select_journal:
        journal = OUTCOME_JOURNALS_DICT[select_journal]
        select_partner = st.selectbox("Select Partner", options = json_data[journal].keys(), index=None)

        if select_partner:
            existing_case_story = check_case_story_exists(
                document_type = "Outcome Journals",
                journal_name = journal,
                partner_name = select_partner
            )

            if existing_case_story:
                case_story = existing_case_story["case_story"]
                with st.spinner(f"Generating case story for {select_partner} from {select_journal}..."):
                    time.sleep(2)
                    st.write_stream(stream_data(case_story))

            else:
                text = json_data[journal][select_partner]
                with st.spinner(f"Generating case story for {select_partner} from {select_journal}..."):
                    case_story = summarize_helper(text = text)
                    if case_story:
                        st.write_stream(stream_data(case_story))
                        store_case_story(
                            case_story = case_story,
                            document_type = "Outcome Journals",
                            journal_name = journal,
                            partner_name = select_partner
                        )

       


else:
    json_data = load_dict_from_json(PROGRESS_REPORT_PARTNERS_PATH)

    select_pdf = st.selectbox("Select PDF", options = PROGRESS_REPORT_PARTNERS_DICT.keys(), index = None)
    if select_pdf:
        pdf = PROGRESS_REPORT_PARTNERS_DICT[select_pdf]
        existing_case_story = check_case_story_exists(
                document_type = "Progess Report Partners",
                pdf_name = pdf
            )
        if existing_case_story:
                case_story = existing_case_story["case_story"]
                with st.spinner(f"Generating case story for {select_pdf}..."):
                    time.sleep(2)
                    st.write_stream(stream_data(case_story))

        else:
            text = json_data[pdf]
            with st.spinner(f"Generating case story for {select_pdf}..."):
                case_story = summarize_helper(text = text)
                if case_story:
                    st.write_stream(stream_data(case_story))
                    store_case_story(
                            case_story = case_story,
                            document_type = "Progess Report Partners",
                            pdf_name = pdf
                        )
        
 
