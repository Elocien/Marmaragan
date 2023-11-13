from util import *
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
import re
import logging


# Params
# ---------------------------------------------------------------------------
# Model
llm_model = "gpt-4-1106-preview"  # "gpt-3.5-turbo-1106" | "gpt-4-1106-preview"
llm_temperature = 0

# ADA/SPARK2014 Project Location
project_location = "/Users/lucian/Documents/Uni/Projects/Diplomarbeit/spark_by_example"

# Input Files

# The file with given to the LLM as a prompt. Should be formatted to remove annotations and possibly provide comments on where to insert spark annotations
source_file = 'ada files/lower_bound/search_lower_bound_p.ads'

# Optional: Can be included in the prompt to provide either the .ads or .adb file, as context for the LLM to work with
context_file = 'ada files/lower_bound/original_search_lower_bound_p.adb'

# The project file to be overwritten with the LLM output. Should be identical to source, excepting the removed annotations and possible comments
destination_file = '/Users/lucian/Documents/Uni/Projects/Diplomarbeit/spark_by_example/binary-search/search_lower_bound_p.ads'


# Prompt Text
prompt_text = "Write an appropriate Pre condition for the supplied .ads specification file in ada/spark2014, so that gnatprove may be run without errors. Return only the full specification file with the Pre condition implemented"
# ---------------------------------------------------------------------------


# Logging Setup
# Set up the logger
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


# Convert given ada file into a prompt template (.json)
ada_to_json(source_file, prompt_text, context_file)


# Load the prompt
prompt = get_prompt("prompt.json")


# Get the LLM Response
llm = ChatOpenAI(model_name=llm_model, temperature=llm_temperature)

response = ""
tokens = ""

with get_openai_callback() as cb:
    response = llm.predict(prompt)
    print(cb)
    tokens = re.findall(r"Tokens Used: (\d+)", str(cb)
                        )[0] if re.findall(r"Tokens Used: (\d+)", str(cb)) else "Error"

# Retrieve the code from the LLM output, removing excess text and other ada code blocks (after the first)
sanitized_response = sanitize_output(response)


# If the response contains ada code, continue, otherwise skip overwriting and gnatprove checking
if sanitized_response is not None:

    # Take the response and write to file
    overwrite_destination_file_with_string(
        destination_file, sanitized_response)

    # Performs a check to see whether any lines in the file have been changed, outside of the given code block,
    # where the annotation should take place
    is_valid_modification = compare_files_and_check(source_file, destination_file)

    # Catch if code beyond the generated annotations has been modified
    if is_valid_modification:

        # Compile the project using Alire
        gnatprove_output, prcoess_returncode = run_gnatprove(project_location)
        
        
        
        
        # SWITCH: If compilation fails
        # 1. Record result
        # 2. Generate new LLM response and try again
    
        # Log 
        logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput Source File: {source_file} \nInput Context File: {context_file}\nPrompt: \n{prompt} \n\nLLM Response: \n{response}\n\nGnatProve Output: \n{gnatprove_output}\n\n")

    
    else:
        # Log illegal modification
        logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput Source File: {source_file} \nInput Context File: {context_file}\nPrompt: \n{prompt} \n\nLLM Response: \n{response}\n\nGnatProve Output: \nILLEGAL FILE MODIFICATION:\nThere were changes to the original file beyond a section of successive lines and the removal of comments. See 'compare_files_and_check' function for the exact specification\n\n")


# If the sanitization of the response fails, log but don't execute gnatprove
else:
    # Log failure of sanitization
    logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput Source File: {source_file} \nInput Context File: {context_file}\nPrompt: \n{prompt} \n\nLLM Response: \n{response}\n\nGnatProve Output: \nGnatprove was not run, the LLM response contained no ADA code, or there was some error sanitizing the response\n\n")
