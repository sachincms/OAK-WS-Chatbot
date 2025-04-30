import streamlit as st
from utils.generate_case_story import summarize_helper
from utils.files_processing import load_dict_from_json
from utils.case_story_db import check_case_story_exists, store_case_story
from config import OUTCOME_JOURNALS_PATH, PROGRESS_REPORT_PARTNERS_PATH


st.set_page_config(page_title = "Case Stories", layout = "wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please log in first")
    st.stop()


main_document = st.radio("Select main document", ["Outcome Journals", "Progess Report Partners"])

if main_document == "Outcome Journals":
    json_data = load_dict_from_json(OUTCOME_JOURNALS_PATH)

    select_journal = st.selectbox("Select Journal", options = json_data.keys())
    if select_journal:
        select_partner = st.selectbox("Select Partner", options = json_data[select_journal].keys(), index=None)

        if select_partner:
            existing_case_story = check_case_story_exists(
                document_type = "Outcome Journals",
                journal_name = select_journal,
                partner_name = select_partner
            )

            if existing_case_story:
                case_story = existing_case_story["case_story"]
                st.success("Loading existing summary from database")
                st.write(case_story)

            else:
                text = json_data[select_journal][select_partner]
                with st.spinner(f"Generating case story for Partner: {select_partner} of Journal: {select_journal}..."):
                    case_story = summarize_helper(text = text)
                    if case_story:
                        st.write(case_story)
                        store_case_story(
                            case_story = case_story,
                            document_type = "Outcome Journals",
                            journal_name = select_journal,
                            partner_name = select_partner
                        )

       


else:
    json_data = load_dict_from_json(PROGRESS_REPORT_PARTNERS_PATH)

    select_pdf = st.selectbox("Select PDF", options = json_data.keys(), index = None)
    if select_pdf:
        existing_case_story = check_case_story_exists(
                document_type = "Progess Report Partners",
                pdf_name = select_pdf
            )
        if existing_case_story:
                case_story = existing_case_story["case_story"]
                st.success("Loading existing summary from database")
                st.write(case_story)

        else:
            text = json_data[select_pdf]
            with st.spinner(f"Generating case story for PDF: {select_pdf}..."):
                case_story = summarize_helper(text = text)
                if case_story:
                    st.write(case_story)
                    store_case_story(
                            case_story = case_story,
                            document_type = "Progess Report Partners",
                            pdf_name = select_pdf
                        )
        
 
