import json

def ada_to_json(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    data = {
        "_type": "prompt",
        "template": f"Add appropriate pragma Loop_Invariant statements to the following ada/spark2014 code, so that gnatprove may be run without errors. Only return the code.\n\n'''ada\n{content}\n'''"
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

# Replace 'input_file_name' and 'output_file_name' with your file names
input_file_name = '/Users/lucian/Documents/Uni/Projects/Diplomarbeit/spark_by_example/binary-search/search_lower_bound_p.adb'
output_file_name = 'prompt.json'

ada_to_json(input_file_name, output_file_name)
