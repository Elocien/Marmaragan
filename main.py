from util import *
import re
import logging


# Params
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------


# Logging Setup
# Set up the logger
logging.basicConfig(filename='history.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')






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
        
        print("\n\nPOTENTIAL ILLEGAL FILE MODIFICATION:\nThere were changes to the original file beyond a section of successive lines and the removal of comments. See 'compare_files_and_check' function for the exact specification\n\n")
        
        # Still run Gnatprove
        gnatprove_output, prcoess_returncode = run_gnatprove(project_location)
        
        
        # Log illegal modification
        logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput Source File: {source_file} \nInput Context File: {context_file}\nPrompt: \n{prompt} \n\nLLM Response: \n{response}\n\nGnatProve Output: \n{gnatprove_output}\n\nError: \nPotential ILLEGAL FILE MODIFICATION:\nThere were changes to the original file beyond a section of successive lines and the removal of comments. See 'compare_files_and_check' function for the exact specification\n\n")


# If the sanitization of the response fails, log but don't execute gnatprove
else:
    # Log failure of sanitization
    logging.info(f" Model: {llm_model} | Temperature: {llm_temperature} | Tokens Consumed: {tokens} \nUser Message: {prompt_text} \nInput Source File: {source_file} \nInput Context File: {context_file}\nPrompt: \n{prompt} \n\nLLM Response: \n{response}\n\nGnatProve Output: \nGnatprove was not run, the LLM response contained no ADA code, or there was some error sanitizing the response\n\n")