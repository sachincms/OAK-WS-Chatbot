from typing import List, Tuple
from llama_index.core import  Document
from typing import List
import os
import llama_index
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv



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

def get_all_sheet_names(file_path: str) -> List[str]:
  '''
  This function returns all sheet names in a given excel file
  Args:
    file path
  Returns:
    list containing all sheet names
    '''
  xls = pd.ExcelFile(file_path)
  sheet_names = xls.sheet_names
  return sheet_names

def get_single_sheet_inside_excel(file_path: str, sheet_name: str):
  '''
  This function returns the dataframe from execl file & a given sheet
  Args:
    file path, sheet name
  Returns:
    dataframe of that given sheet
    '''
  df = pd.read_excel(file_path, sheet_name)
  columns_to_be_dropped = [col for col in df.columns if col.startswith("Unnamed")]
  df = df.drop(columns_to_be_dropped, axis = 1)
  return df


################################################ FOR CHAT PROMPT TEMPLATE ##################################################################################

def convert_the_excel_file_into_dict(excel_file_path: str,
                                     json_file_path: str) -> dict:
  '''
  This function converts the entire excel file in a dict. 
  Also checks the current json file & only adds new sheets which aren't present in the current json file
  Args:
    excel file path, json file path
  Returns:
    dictionary containing keys as sheet names & values as a dictionary of dataframe
  '''

  #load the current json file
  current_dict = load_dict_from_json(json_file_path)
  current_sheet_names = current_dict.keys()


  #get all sheet names
  sheet_names = get_all_sheet_names(excel_file_path)
  
  #find the new sheets
  new_sheets = [sheet for sheet in sheet_names if sheet not in current_sheet_names]
  print(f"New sheets to add: {len(new_sheets)}")

  #iterate through all sheets & convert each sheet into dictionary of records
  for sheet in new_sheets:
    print(f"Preprocessing sheet: {sheet}")
    try:
      df = get_single_sheet_inside_excel(excel_file_path, sheet)
      dict_ = df.to_dict(orient = "records")
      current_dict[sheet] = dict_
    except Exception as e:
      print(f"Error in sheet: {sheet}. Error: {e}.\nMoving on to the next one.....")

  return current_dict
  

################################################ FOR LLAMAINDEX DOCUMENTS ##################################################################################

def convert_dataframe_into_dict_and_llamaindex_docs(file_path: str,
                                                    sheet_name: str) -> Tuple[List[dict], List[llama_index.core.schema.Document]]:
    '''
    This function converts the single sheet inside excel file into dictionary records (for chat prompt) & llamaindex documents (for embeddings)
    Args:
      file path, sheet name
    Returns:
      dictionary records (for chat prompt) & llamaindex documents (for embeddings)
    '''
    df = get_single_sheet_inside_excel(file_path, sheet_name)

    #this is for Gemini prompt
    dict_ = df.to_dict(orient = "records")

    #this is for LlamaIndex documents & OpenAI
    documents = []
    for entry in dict_:
      cleaned_entry = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in entry.items()}
      text = "\n".join(f"{key}:{value}" for key, value in cleaned_entry.items())
      doc = Document(text=text)
      doc.metadata = {"file_name": os.path.basename(file_path),
                     "sheet": sheet_name}
      documents.append(doc)

    return dict_, documents









