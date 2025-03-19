from typing import List
from llama_index.core import  VectorStoreIndex
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini
from typing import List
import numpy as np
import os
import sys
import llama_index
import nest_asyncio
from config import *
from utils.evaluate_chat import *
import re
from typing import Tuple
from dotenv import load_dotenv
import time
from requests.exceptions import HTTPError
from logging_config import get_logger


load_dotenv()
nest_asyncio.apply()

logger = get_logger(__name__)


def switch_google_api_key(current_index: int):
   """
    Switch to the next API key in the list.
    Args:
        current_index (int): The index of the current API key.
    Returns:
        int: The new API key index.
    Raises:
        IndexError: If all API keys have been exhausted.
    """
   new_index = current_index + 1
   if new_index >= len(GOOGLE_API_KEYS):
      raise IndexError("All API keys are exhausted")
   
   new_key = GOOGLE_API_KEYS[new_index]
   os.environ["GOOGLE_API_KEY"] = new_key
   logger.warning(f"{GOOGLE_API_KEYS[current_index]} rate limit exceeded. Switching to {new_key}")
   return new_index
   


####################################### IF VECTOR EMBEDDINGS ARE USED ########################################################################
def create_chat_engine(vector_index: VectorStoreIndex):
   '''
  This function create dthe chat engine
  Args:
    vector store index
  Returns:
    chat engine (current based on OpenAI)
  '''
   llm = OpenAI(model = OPENAI_MODEL_NAME)
   chat_engine = vector_index.as_chat_engine(chat_mode = "best", llm = llm, verbose = True)
   return chat_engine


def qa_chat_pdf(chat_engine, query: str) -> str:
   
    '''
  This functions returns the answer & source of the answer to a question
  Args:
     chat engine, query
  Returns:
    answer & its source to the given query
   '''

    result = chat_engine.chat(query)
    answer = result.response
    source_nodes = result.source_nodes
    faithfulness = check_faithfulness(query, result)
    relevancy = check_relevancy(query, result)
    source_dict = {}
    scores = []
   
    for i in range(0, len(source_nodes)):
      source_document = os.path.basename(source_nodes[i].metadata["source"])
      page_number = source_nodes[i].metadata["page_label"]
      scores.append(source_nodes[i].score)

      if source_document not in source_dict:
        source_dict[source_document] = []

      if page_number not in source_dict[source_document]:
        source_dict[source_document].append(page_number)

    scores = np.array(scores)
    if scores.mean() >= NODE_THRESHOLD and faithfulness and relevancy:
        return answer, source_dict
    else:
        answer = None
        source_dict = None
        return answer, source_dict


def qa_chat_excel(chat_engine, query: str) -> dict:
  '''
  This functions initiations the questions-answering & stoes it as a tuple in a list
  Args:
     chat engine, chat history
  Returns:
    chat history containing all questions and answers along with their sources & stores as a dictionary
  '''
  d = {}

  result = chat_engine.chat(query)
  d["query"] = query
  answer = result.response
  source_nodes = result.source_nodes
  faithfulness = check_faithfulness(query, result)
  relevancy = check_relevancy(query, result)

  source_dict = {}
  scores = []

  for i in range(0, len(source_nodes)):
    source_file = source_nodes[i].metadata["file_name"]
    scores.append(source_nodes[i].score)

    if source_file not in source_dict:
      source_dict[source_file] = []

    source_sheet = source_nodes[i].metadata["sheet"]
    if source_sheet not in source_dict[source_file]:
      source_dict[source_file].append(source_sheet)

  scores = np.array(scores)
  if scores.mean() >= 0.5 and faithfulness and relevancy:
      return answer, source_dict
  else:
      answer = None
      source_dict = None
      return answer, source_dict
    


####################################### IF CHAT PROMPT TEMPLATE IS USED ###############################################
def convert_query_into_chat_message(text: str, query: str) -> List[llama_index.core.base.llms.types.ChatMessage]:
  '''
  This function converts the input text & query into chat message template
  Args:
    Input context text & query
  Returns:
    Chat Message template 
  '''
  
  template = (
      "The following text consists of some context, a question and some instructions. Use the context to answer the question and follow the instructions while doing so."
      "\n----------- Start of Context ----------\n"
      "{context_str}"
      "\n---------- End of Context -----------\n"

      "\n----------- Start of Question ----------\n"
      "{query_str}"
      "\n----------- End of Question ----------\n"

      "\n----------- Start of Instructions ----------\n"
      "When answering, please provide relevant supporting details and cite the specific part of the context where the answer is derived from."
      "Try to rephrase or summarize the relevant supporting details in your answer instead of using the exact same wording as present in the context."
      "Make sure your answer responds to the query being asked and does not contain irrelevant information or spelling mistakes."
      "Your answer should be concise and to the point while including all necessary details."
      "Try not to use too many bullet points, only use them when necessary."
      "Your entire answer should not be longer than 500 words."
      "Please provide the answer in the following format:\n"
      "Answer: <Your answer here>\n"
      "Source: <Reference to relevant part of the context>"
      "If answer is not found in the provided context then reply exactly with:\n"
      "'Answer not found from the given context provided.'"
      "\n----------- End of Instructions ----------\n"
  )
  qa_template = PromptTemplate(template)

  messages = qa_template.format_messages(context_str = text, query_str = query)
  return messages


def split_answer_and_sources(text: str) -> Tuple[str, str]:
  '''
  This function splits the answer & text from response text
  Args:
    response text
  Returns:
    answer & source
  '''
  pattern1 = r"(.*)\s*\(Source: (.*)\)"
  pattern2 = r"Answer:\s*(.*)\s*\nSource: (.*)"

  matches = re.findall(pattern1, text, re.DOTALL)
  if not matches:
    matches = re.findall(pattern2, text, re.DOTALL)

  answers_list = []
  sources_list = set()

  for answer, source in matches:
    answers_list.append(answer.strip())

    for s in source.split(";"):
      sources_list.add(s.strip())

  final_answer = "\n".join(answers_list)
  final_answer = final_answer.split("Answer:")[-1]
  final_source = "\n".join(sorted(sources_list))
  return final_answer, final_source


def qa_chat_with_prompt(text: str, query: str) -> dict:
  '''
  This function returns a dictionary containing answer & source
  Args:
    Input context text & query
  Returns:
    Dictionary containing query, answer, source
  '''
  messages = convert_query_into_chat_message(text = text, 
                                           query = query)
  current_index = 0
  os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEYS[current_index]
  while True: 
     try:
        llm = Gemini(model = GEMINI_MODEL_NAME)
        resp = llm.chat(messages)  #llama_index.core.base.llms.types.ChatResponse

        result_text = resp.message.blocks[0].text

        d = {}
        d["query"] = query

        if "Source:" in result_text:
          answer, source = split_answer_and_sources(result_text)
          d["answer"] = answer
          d["source"] = source
        else:
          d["answer"] = result_text
          d["source"] = None

        return d
     
     except HTTPError as e:
        if e.response.status_code == 429:
            try:
              current_index = switch_google_api_key(current_index)
              time.sleep(2)
            except IndexError:
               raise ValueError("All API keys are exhausted or invalid")
        else:
           raise e

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)
