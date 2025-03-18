from typing import List, Tuple
from llama_index.core import  Document
from typing import List
import os
import llama_index
import pandas as pd
import json
from datetime import datetime
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from logging_config import get_logger

logger = get_logger(__name__)

def custom_serializer(obj):
    """
    Serialize non-JSON serializable objects, such as datetime.
    Args:
        obj (any): The object to serialize.
    Returns:
        str: An ISO 8601 formatted string if the object is a datetime instance.
    Raises:
        TypeError: If the object type is not supported for serialization.
    """
    if isinstance(obj, datetime):
      return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")


def save_dict_to_json(input_dict: dict, file_path: str):
  '''
  This function saves the dictionary to JSON file
  Args:
    input dictionary, file path
  Returns:
    None
  '''
  with open(file_path, "w") as f:
    json.dump(input_dict, f, default=custom_serializer)

def load_dict_from_json(file_path: str) -> dict:
  '''
  This function loads the dictionary from json file
  Args:
    file path
  Returns:
    dictionary
  '''
  with open(file_path, "r") as f:
    loaded_dict  = json.load(f)
  return loaded_dict


################################################ EXCEL PROCESSING ##################################################################################

def authenticate_gspread(gdrive_credentials_path: str) -> gspread.client.Client:
  """Authenticate with Google Sheets using the service account JSON key."""
  scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
  creds = ServiceAccountCredentials.from_json_keyfile_name(gdrive_credentials_path, scope)
  client = gspread.authorize(creds)
  return client


def get_all_sheet_names(spreadsheet_id: str, 
                        client: gspread.client.Client) -> List[str]:
  '''
  This function returns all sheet names in a given excel file
  Args:
    spreadsheet id, client
  Returns:
    list containing all sheet names
  '''
  spreadsheet = client.open_by_key(spreadsheet_id)
  return [sheet.title for sheet in spreadsheet.worksheets()]


def get_single_sheet_from_spreadsheet(spreadsheet_id: str, 
                                      sheet_name: str, 
                                      client: gspread.client.Client):
  '''
  This function returns the dataframe from execl file & a given sheet
  Args:
    spreadsheet id, sheet name, client
  Returns:
    dataframe of that given sheet
  '''
  spreadsheet = client.open_by_key(spreadsheet_id)
  worksheet = spreadsheet.worksheet(sheet_name)
  df = get_as_dataframe(worksheet, evaluate_formulas=True, header=0)
  return df.dropna(how="all")  # Drop empty rows


################################################ FOR CHAT PROMPT TEMPLATE ##################################################################################

def convert_excel_to_dict(spreadsheet_id: str,
                                     json_file_path: str,
                                     gdrive_credentials_path: str) -> dict:
  '''
  This function converts the entire excel file in a dict.
  Also checks the current json file & only adds new sheets which aren't present in the current json file
  Args:
    spreadsheet id, json file path, gdrive credentials path
  Returns:
    dictionary containing keys as sheet names & values as a dictionary of dataframe
  '''
  client = authenticate_gspread(gdrive_credentials_path)

  #load the current json file
  if os.path.exists(json_file_path):
    try:
      current_dict = load_dict_from_json(json_file_path)
      current_sheet_names = current_dict.keys()
    except Exception:
      logger.warning("Error reading JSON file. Initilazing as empty")
      current_dict = {}
      current_sheet_names = set()
  else:
    logger.warning("JSON file does not exist. Extracting all sheets....")
    current_dict = {}
    current_sheet_names = set()


  #get all sheet names
  sheet_names = get_all_sheet_names(spreadsheet_id, client)

  #find the new sheets
  new_sheets = [sheet for sheet in sheet_names if sheet not in current_sheet_names]
  logger.info(f"New sheets to add: {len(new_sheets)}")

  #iterate through all sheets & convert each sheet into dictionary of records
  for sheet in new_sheets:
    logger.info(f"Preprocessing sheet: {sheet}")
    try:
      df = get_single_sheet_from_spreadsheet(spreadsheet_id, sheet)
      dict_ = df.to_dict(orient = "records")
      current_dict[sheet] = dict_
    except Exception as e:
      logger.error(f"Error in sheet: {sheet}. Moving on to the next one.....")
        
  return current_dict