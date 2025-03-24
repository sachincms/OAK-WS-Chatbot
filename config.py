import os

# OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
# OPENAI_MODEL_NAME = "gpt-3.5-turbo"
GEMINI_MODEL_NAME = "models/gemini-2.0-flash"
EMBED_DIMENSION = 512
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 50
NODE_THRESHOLD = 0.5

current_file_path = os.getcwd()
LOGO_STYLE_HTML = os.path.join(current_file_path, "static",  "html", "logo_style.html")

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

INTRO_MESSAGE = """
India has over 172 million children at risk of harm, despite strong child protection laws. 
To tackle this, COF-KAWACH—a 10-year initiative by the British Asian Trust (BAT) and its partners—was launched in June 2022. 
The program works across Bihar, Uttar Pradesh, West Bengal, and Rajasthan, strengthening systems from grassroots to state levels to prevent child exploitation. 
By collaborating with local NGOs and government bodies, KAWACH aligns with India’s Mission Vatsalya to create safer childhoods.
"""
INTRO_MARKDOWN = """
<p>Ask anything about OAK:</p>
<ul>
<li>Which of the following is a source of information for assessing partners' challenges?</li>
<li>Which metric is used to assess the likelihood of shared outcomes being sustained over time?</li>
<li>How can proxies be used to evaluate shared outcomes across organizations working in the same geography?</li>
<strong>Powered by real data & reports. Available anytime.</strong>
"""

DEFAULT_QUERY = "What specific program activities, such as trade meetings and SSK camps, may have contributed to the change in behavior of the members towards accessing their PF benefits?"
DEFAULT_QUERY_RESPONSE = "Trade meetings and SSK camps may have contributed to the change in behavior of the members towards accessing their PF benefits by raising awareness about the importance of knowing their UAN numbers.  After awareness sessions and camps on PF, members collectively approached mahajans for their UAN numbers."
DEFAULT_RESPONSE_SOURCE = 'The section describing the experience of women unorganized sector workers in Raghunathganj II states: "In Raghunathganj II beedi members are entitled to PF benefit but one major concern that came up while accessing PF benefits were that the members were not aware of their UAN no. due to which there were not able to access their PF accounts when needed. After awareness sessions and camps on PF, Members collectively approached mahajans for UAN no."'
DEFAULT_FINAL_RESPONSE = f"\n{DEFAULT_QUERY_RESPONSE}\n\n**Source:** {DEFAULT_RESPONSE_SOURCE}"
ERROR_MESSAGE = "An error occurred while processing your request. Please try again later."