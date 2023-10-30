import json

def ada_to_json(input_file, prompt_text):
    """
    Takes an .adb file as input in order to generate an LLM prompt which can be loaded by langchain
    """
    
    with open(input_file, 'r') as f:
        content = f.read()

    data = {
        "_type": "prompt",
        "input_variables":[],
        "template": f"{prompt_text}.\n\n'''ada\n{content}\n'''"
    }

    with open('prompt.json', 'w') as f:
        json.dump(data, f, indent=4)
