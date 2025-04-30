import llama_index
from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini
from llama_index.core.base.llms.types import ChatMessage
from requests.exceptions import HTTPError, ConnectionError, Timeout
from time import time
from typing import List
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger
from config import GOOGLE_API_KEYS, GEMINI_MODEL_NAME, OUTCOME_JOURNALS_PATH, PROGRESS_REPORT_PARTNERS_PATH
from utils.chat import switch_google_api_key
from utils.files_processing import load_dict_from_json
from utils.case_story_db import store_case_story

logger = get_logger(__name__)

def convert_query_into_chat(text: str) -> List[llama_index.core.base.llms.types.ChatMessage]:
    '''
    This function converts the input text & query into chat message template
    Args:
      Input context text & query
    Returns:
      Chat Message template 
     '''

    prompt_template_str = (
    "You are a development impact writer. Based on the context below, generate a NEW case story. "
    "Use a compelling, human-centered tone. Structure it with:\n"
    '''
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
    '''

    "DO NOT copy any part of the example used earlier. Only use facts and ideas from the context.\n\n"
    "----------- CONTEXT -----------\n"
    "{context_str}\n"
    "----------- END CONTEXT -----------\n\n"
    "Start your case story below:"
    )
    prompt = PromptTemplate(prompt_template_str)
    prompt_text = prompt.format(context_str=text)
    return [ChatMessage(role="user", content=prompt_text)]


def summarize_helper(text: str) -> str:
    '''
    This function generates case story
    Args:
      Input text 
    Returns:
      case story 
     '''
    message = convert_query_into_chat(text)

    current_index = 0
    while True:
        try:
            api_key = GOOGLE_API_KEYS[0]
            llm = Gemini(model = GEMINI_MODEL_NAME, api_key = api_key)
            response = llm.chat(message)
            try:
                return response.message.content.strip()
            except Exception as ex:
                logger.error(f"Error: {ex}")
                return response.text.strip()
            
        except HTTPError as e:
            if e.response.status_code == 429:
                try:
                    current_index = switch_google_api_key(current_index)
                    time.sleep(2)
                except ValueError:
                    raise ValueError("All API keys are exhausted or invalid.")
                
            elif e.response.status_code in [501, 502, 503, 504]:
                logger.error(f"Server error {e.response.status_code}: {e.response.text}")
                return  None
        
            elif e.response.status_code in [401, 401, 403, 404]:
                logger.error(f"Client error {e.response.status_code}: {e.response.text}")
                return  None
            else:
                raise e 
        
        except (ConnectionError, Timeout) as e:
            logger.error(f"Network error: {str(e)}")
            return  None
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return  None

            
def generate_all_case_stories():
    outcome_journals = load_dict_from_json(OUTCOME_JOURNALS_PATH)
    progress_report_partners = load_dict_from_json(PROGRESS_REPORT_PARTNERS_PATH)

    for journal in outcome_journals.keys():
        for partner in outcome_journals[journal].keys():
            context = outcome_journals[journal][partner]
            case_story = summarize_helper(text = context)
            store_case_story(
                case_story = case_story,
                document_type = "Outcome Journals",
                journal_name = journal,
                overwrite = True
            )
    
    for pdf in progress_report_partners.keys():
        context = progress_report_partners[pdf]
        case_story = summarize_helper(text = context)
        store_case_story(
            case_story = case_story,
            document_type = "Progess Report Partners",
            pdf_name = pdf,
            overwrite = True
        )
    
    # text = json_data[select_pdf]
    #         with st.spinner(f"Generating case story for PDF: {select_pdf}..."):
    #             case_story = summarize_helper(text = text)
    #             if case_story:
    #                 st.write(case_story)
    #                 store_case_story(
    #                         case_story = case_story,
    #                         document_type = "Progess Report Partners",
    #                         pdf_name = select_pdf
    #                     )

if __name__ == "__main__":
    generate_all_case_stories()