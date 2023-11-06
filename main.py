from langchain.chat_models import ChatOpenAI
from util import *
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
import re

import logging



#Params
# ---------------------------------------------------------------------------
# Model
llm_model = "gpt-3.5-turbo-0613" #or "gpt-4"
llm_temperature = 0

# ADA/SPARK2014 Project Location
project_location = "/Users/lucian/Documents/Uni/Projects/Diplomarbeit/spark_by_example"

# Input File
input_file = '/Users/lucian/Documents/Uni/Projects/Diplomarbeit/spark_by_example/binary-search/search_lower_bound_p.adb'

# Prompt Text
prompt_text = "Add appropriate pragma Loop_Invariant statements to the following ada/spark2014 code, so that gnatprove may be run without errors. Only return the code"
# ---------------------------------------------------------------------------




# Logging Setup
# Set up the logger
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')





# Convert given ada file into a prompt template (.json)
ada_to_json(input_file, prompt_text)


# Load the prompt
prompt = get_prompt("prompt.json")

# Get the LLM Response
llm = ChatOpenAI(model_name=llm_model, temperature=llm_temperature)
    




# LLM STUFF
# TODO: Format and make pretty
response = ""
tokens = ""
    
with get_openai_callback() as cb:
    response = llm.predict(prompt)
    # response = sanitize_output(llm.predict(prompt))
    tokens = re.findall(r"Tokens Used: (\d+)", str(cb))[0] if re.findall(r"Tokens Used: (\d+)", str(cb)) else "Error"



# Take the response and write to file
overwrite_ada_file(input_file, response)

# Compile the project using Alire 
gnatprove_output = run_gnatprove(project_location)

# SWITCH: If compilation fails
    # 1. Record result 
    # 2. Generate new LLM response and try again 
    




# Log
logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput File: {input_file} \nLLM Response: \n{response}\nGnatProve Output: \n\n")