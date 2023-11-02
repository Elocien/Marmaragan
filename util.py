from langchain.prompts import load_prompt
import json
import os
import subprocess




def ada_to_json(input_file, prompt_text):
    """
    Takes an .adb file as input in order to generate an LLM prompt which is written to a JSON file
    """
    valid_extensions = ('.adb', '.ads')
    
    # Extract the file extension from the input_file path
    file_extension = os.path.splitext(input_file)[1]

    # Check if the file extension is either .adb or .ads
    if file_extension not in valid_extensions:
        raise ValueError("Invalid file extension. Please provide a file with .adb or .ads extension.")

    
    with open(input_file, 'r') as f:
        content = f.read()

    data = {
        "_type": "prompt",
        "input_variables":[],
        "template": f"{prompt_text}.\n\n'''ada\n{content}\n'''"
    }

    with open('prompt.json', 'w') as f:
        json.dump(data, f, indent=4)


def get_prompt(file_name):
    """
    Loads the prompt which is passed to the LLM from a JSON file. 
    """
    prompt = load_prompt(file_name)
    
    return prompt.format()



def sanitize_output(text: str):
    '''
    TODO: Implement this to catch instances where the prompt contains content other than ada code
    '''
    _, after = text.split("```ada")
    return after.split("```")[0]



def overwrite_ada_file(file_path, new_string):
    '''
    Overwrites the input ada file with new content (in this case LLM output)
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(new_string)
    except IOError:
        print(f"An error occurred while trying to overwrite the file {file_path}.")





def run_gnatprove(file_location):
    '''
    TODO: catch complete error message from gnatprove
    Starts a subprocess and executes 'alr gnatprove' on a given directory
    '''
    try:
        result = subprocess.run(["alr", "gnatprove", file_location], capture_output=True, text=True, check=True)
        print("alr gnatprove was run")
        print("Standard Output:")
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("An error occurred while running alr gnatprove:")
        if e.stderr:
            error_message = f"Error Message: {e.stderr}"
            print(error_message)
            return error_message
        else:
            error_message = f"An error occurred: {e}"
            print(error_message)
            return error_message
