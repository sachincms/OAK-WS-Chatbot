import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CASE_STORY_COLLECTION
from handlers.MongoDBHandler import MongoDBHandler
from logging_config import get_logger

logger = get_logger(__name__)


mongodb_handler = MongoDBHandler(CASE_STORY_COLLECTION)


def check_case_story_exists(document_type: str,
                            journal_name: str = None,
                            partner_name: str = None,
                            pdf_name: str = None):
    if document_type == "Outcome Journals":
        query = {
            "document_type" : document_type,
            "journal_name": journal_name,
            "partner_name": partner_name
        }
    else:
        query = {
            "document_type" : document_type,
            "pdf_name": pdf_name
        }

    results = mongodb_handler.read_data(query)
    if results:
        return results[0]
    return None


def store_case_story(
        case_story: str,
        document_type: str,
        journal_name: str = None,
        partner_name: str = None,
        pdf_name: str = None,
        overwrite: bool = False
    ):
    if document_type == "Outcome Journals":
        data = {
            'document_type': document_type,
            'journal_name': journal_name,
            'partner_name': partner_name,
            'case_story': case_story
        }
        query = {'document_type': document_type, 'journal_name': journal_name, 'partner_name': partner_name}
    else:
        data = {
            'document_type': document_type,
            'pdf_name': pdf_name,
            'case_story': case_story
        }
        query = {'document_type': document_type, 'pdf_name': pdf_name}

    if overwrite:
        mongodb_handler.insert_data(data)
        logger.info(f"Inserted case story for {journal_name} and {partner_name} or {pdf_name}")
        return
    
    existing_case_story = check_case_story_exists(query)
    if not existing_case_story:
        mongodb_handler.insert_data(data)