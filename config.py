import os
from dotenv import load_dotenv

load_dotenv()

# OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
# OPENAI_MODEL_NAME = "gpt-3.5-turbo"
GEMINI_MODEL_NAME = "models/gemini-2.0-flash"
EMBED_DIMENSION = 512
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 50
NODE_THRESHOLD = 0.5

current_file_path = os.getcwd()
LOGO_STYLE_HTML = os.path.join(current_file_path, "static",  "html", "logo_style.html")
LOGOUT_BUTTON_STYLE = os.path.join(current_file_path, "static",  "html", "logout_button_style.html")
AUTH_CONTAINER_STYLE = os.path.join(current_file_path, "static",  "html", "auth_container_style.html")

MONGODB_URI = os.getenv("MONGODB_URI")
SPF_DATABASE = os.getenv("SPF_DATABASE")
USER_COLLECTION = os.getenv("USER_COLLECTION")
CASE_STORY_COLLECTION = os.getenv("CASE_STORY_COLLECTION")

# OAK_LOGO_PATH = os.path.join(current_file_path, "static",  "images", "Oak.png")
# CMS_LOGO_PATH = os.path.join(current_file_path, "static",  "images", "CMS.png")
#TODO: Replace PNG with SVG
SPF_LOGO_PATH = os.path.join(current_file_path, "static",  "images", "SPF.png")
SWASTI_LOGO_PATH = os.path.join(current_file_path, "static",  "images", "Swasti.png") 

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
PHASE1_JSON_FILE_PATH = os.path.join(current_file_path, "data", "phase1.json")
PHASE2_JSON_FILE_PATH = os.path.join(current_file_path, "data", "phase2.json")
PHASE2_WITH_SDD_JSON_FILE_PATH = os.path.join(current_file_path, "data", "phase2_with_sdd.json")
ALL_PHASES_JSON_FILE_PATH = os.path.join(current_file_path, "data", "all_phases.json")
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")

GOOGLE_API_KEY_1 = os.getenv("GOOGLE_API_KEY_1")
GOOGLE_API_KEY_2 = os.getenv("GOOGLE_API_KEY_2")
GOOGLE_API_KEYS = [GOOGLE_API_KEY_1, GOOGLE_API_KEY_2]

LOGS_DIRECTORY = os.path.join(current_file_path, "logs")


DEFAULT_QUERY = "What specific program activities, such as trade meetings and SSK camps, may have contributed to the change in behavior of the members towards accessing their PF benefits?"
DEFAULT_QUERY_RESPONSE = "Trade meetings and SSK camps may have contributed to the change in behavior of the members towards accessing their PF benefits by raising awareness about the importance of knowing their UAN numbers.  After awareness sessions and camps on PF, members collectively approached mahajans for their UAN numbers."
DEFAULT_RESPONSE_SOURCE = 'The section describing the experience of women unorganized sector workers in Raghunathganj II states: "In Raghunathganj II beedi members are entitled to PF benefit but one major concern that came up while accessing PF benefits were that the members were not aware of their UAN no. due to which there were not able to access their PF accounts when needed. After awareness sessions and camps on PF, Members collectively approached mahajans for UAN no."'
DEFAULT_FINAL_RESPONSE = f"\n{DEFAULT_QUERY_RESPONSE}\n\n**Source:** {DEFAULT_RESPONSE_SOURCE}"
ERROR_MESSAGE = "An error occurred while processing your request. Please try again later."

OUTCOME_JOURNALS_PATH = os.path.join(current_file_path, "data", "outcome_journals.json")
PROGRESS_REPORT_PARTNERS_PATH = os.path.join(current_file_path, "data", "progress_report_partners.json")
GAF_PATH = os.path.join(current_file_path, "data", "gaf.json")

SECTION_PATTERNS_FOR_PRR_PDF = {
        "Your organisation’s name": r"(Your organisation’s name:)",
        "Project title": r"(Project title:)",
        "Grant number": r"(Grant number:)",
        "Grant period": r"(Grant period:)",
        "Currency": r"(Currency:)",
        "Total Amount LCY": r"(Total Amount LCY:)",
        "Total Amount USD": r"(Total Amount USD:)",
        "Date of report: (dd/mon/yy)": r"(Date of report: (dd/mon/yy))",
        "Project Location:": r"(Project Location:)",
        "Period covered by this report:": r"(Period covered by this report:)",
        "Progress Reports submitted to date for this grant (including this one):": r"(Progress Reports submitted to date for this grant (including this one):)",
        "Purpose:": r"(Purpose:)",
        "Progress Against Objectives": r"(Progress Against Objectives)",
        "Significant changes": r"(Significant changes.)",
        "Additional question(s)": r"(Additional question(s):)",
        "What has your team learned during the implementation and evaluation of your project?": r"(What has your team learned during the implementation and evaluation of your project?)",
        "How will your team use this information to change the way you work?": r"(How will your team use this information to change the way you work?)",
        "How will you share what you have learned inside and outside your organisation?": r"(How will you share what you have learned inside and outside your organisation?)",
        "II. ATTACHMENTS": r"(II\.\s*ATTACHMENTS|Attachments)",
        "III. TO BE COMPLETED BY OAK STAFF": r"(III\.\s*TO BE COMPLETED BY OAK STAFF|To Be Completed By Oak Staff)"
    }


SECTION_PATTERNS_FOR_PRR_WORD = {
        "One Year Progress Report-2023": r" One Year Progress Report-2023",
        "Project Objective 1: Formation and Strengthening the Village Level Institutions/ Groups while ensuring Women Leadership in these institutions": r"Project Objective 1: Formation and Strengthening the Village Level Institutions/ Groups while ensuring Women Leadership in these institutions",
        "Project Objective 2: Promoting agro-ecological practices, crop diversification and water resource development for food & nutritional security": r"Project Objective 2: Promoting agro-ecological practices, crop diversification and water resource development for food & nutritional security",
        "Project Objective 3: Enhancing access to alternative livelihoods among landless, resource poor and other forest dependent communities": r"Project Objective 3: Enhancing access to alternative livelihoods among landless, resource poor and other forest dependent communities",
        "Project Objective 4: Enabling project communities to access and avail their constitutional rights and entitlements": r"Project Objective 4: Enabling project communities to access and avail their constitutional rights and entitlements",
    }

SECTION_PATTERNS_FOR_GAF_PDF = {
      "1. ORGANISATION": r"1\.\s*ORGANISATION",
    "2. CONTACT INFORMATION": r"(?:2\.\s*(CONTACT\s+INFORMATION|Principal\s+Contact)|3\.\s*Signatory\s+Contact)",
    "3. PROJECT OVERVIEW": r"(?:3\.|4\.)\s*PROJECT\s+OVERVIEW",
    "4. GEOGRAPHY": r"(?:\d+\.)?\s*List\s+the\s+major\s+countries\s+where\s+your\s+activities\s+take\s+place\.\s+If\s+this\s+is\s+global\s+(?:policy\s+)?work,\s+list\s+as\s+worldwide:",
    "5. ORGANISATION CONTEXT": r"(?:5\.|6\.)\s*(ORGANISATION\s+CONTEXT|Context)",
    "6. PLACE HOLDER": r"6\.\s*PLACE\s+HOLDER",
    "7. OBJECTIVES": r"7\.\s*OBJECTIVES",
    "8. COOPERATION": r"8\.\s*COOPERATION",
    "9. MONITORING, EVALUATION & LEARNING": r"(?:9\.|10\.)\s*(MONITORING, EVALUATION\s*&\s*LEARNING|Impact|Evaluation)",
    "10. RISKS AND CHALLENGES": r"10\.\s*RISKS\s+AND\s+CHALLENGES",
    "11. ADDITIONAL QUESTIONS/ Future Plans": r"(?:11\.)\s*(ADDITIONAL\s+QUESTIONS|Future\s+Plans)",
    "12. DECLARATIONS": r"(?:12\.)\s*DECLARATIONS",
    "13. ATTACHMENTS": r"(?:13\.)\s*ATTACHMENTS",
    "14. COMMENTS": r"(?:14\.)\s*(COMMENTS|Submission)",
    "15. Full Name": r"(?:15\.)?\s*Full\s+Name\s+of\s+the\s+person\s+completing\s+the\s+form",
    "16. Date of Submission": r"(?:16\.)?\s*Date\s+of\s+Submission:\s*\(dd/mon/yy\)"

    }