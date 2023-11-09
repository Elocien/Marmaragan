from langchain.prompts import load_prompt
import json
import os
import subprocess
import re
import shutil
import pty
import select
import difflib




def ada_to_json(source_file: str, prompt_text: str, context_file: str = None):
    """
    Takes an .adb file as input and optionally an associated .ads file to generate an LLM prompt 
    which is then written to a JSON file. Each code block from the .adb and .ads files is individually
    delimited with markers for ADA code.
    
    Args:
        input_file (str): The path to the source file.
        prompt_text (str): The text to be used as part of the prompt.
        spec_file (str, optional): The path to the context file. Defaults to None.
        
    Raises:
        ValueError: If the provided input_file does not have an .adb or .ads extension.
    """
    valid_extensions = ('.adb', '.ads')
    
    # Extract the file extension from the input_file path
    input_file_extension = os.path.splitext(source_file)[1]

    # Check if the input_file extension is either .adb or .ads
    if input_file_extension not in valid_extensions:
        raise ValueError("Invalid file extension for the input file. Please provide a file with .adb or .ads extension.")
    
    # Initialize the template content with the prompt text
    template_content = f"{prompt_text}\n\n"

    # Function to read file and enclose content in '''ada
    def read_and_delimit_ada_code(file_path: str):
        with open(file_path, 'r') as file:
            return f"'''ada\n{file.read()}\n'''\n"

    # Add the content of the input_file to the template with delimiters
    template_content += read_and_delimit_ada_code(source_file)
    template_content += read_and_delimit_ada_code(context_file)

    # Construct the data dictionary
    data = {
        "_type": "prompt",
        "input_variables": [],
        "template": template_content.strip()  # Remove the last newline
    }

    # Write the data dictionary to a JSON file
    with open('prompt.json', 'w') as f:
        json.dump(data, f, indent=4)




def get_prompt(file_name : os.path):
    """
    Loads the prompt which is passed to the LLM from a JSON file. 
    """
    return load_prompt(file_name).format()



def sanitize_output(api_output: str):
    """
    Extracts and returns Ada code blocks from the given GPT-4 API output.
    """
    # Define the pattern to capture the code block between '''ada and ''' or ```ada and ```
    pattern = re.compile(r"('''ada(.*?)'''|```ada(.*?)```)", re.DOTALL)

    # Search for the pattern in the input string
    match = pattern.search(api_output)

    # If a match is found, return the code block without the delimiters
    if match:
        # Check if either of the groups has a match
        if match.group(2):
            return match.group(2).strip()
        elif match.group(3):
            return match.group(3).strip()

    # If no match is found, return an empty string or None
    return None



def overwrite_destination_file_with_string(file_path : os.path, content : str):
    '''
    Overwrites the input ada file with new content (in this case LLM output)
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError:
        print(f"An error occurred while trying to overwrite the file {file_path}.")



def overwrite_file(source_path, destination_path):
    """
    Overwrites the content of the destination file with the content of the source file.
    """
    try:
        shutil.copyfile(source_path, destination_path)
    except IOError as e:
        print(f"An error occurred: {e.strerror}")
        
        
def get_file_diff(file_path1, file_path2):
    """
    Compares two text files and returns a string detailing only the differences.

    This function uses the `difflib` module to perform a line-by-line comparison
    between two files, identifying lines that are different. Only lines that are
    added or removed are returned, unchanged lines are omitted.

    Parameters:
    - file_path1 (str): The path to the first file to compare.
    - file_path2 (str): The path to the second file to compare.

    Returns:
    - str: A string containing the line-by-line differences between the two files.
           Lines present only in the first file are prefixed with a '-',
           lines present only in the second file are prefixed with a '+'. 
    """
    # Open and read the files
    with open(file_path1, 'r') as file1:
        file1_text = file1.read().splitlines()

    with open(file_path2, 'r') as file2:
        file2_text = file2.read().splitlines()

    # Create a Differ object and calculate the difference
    differ = difflib.Differ()
    diff_gen = differ.compare(file1_text, file2_text)

    # Filter out lines that have not changed
    diff = [line for line in diff_gen if line.startswith(
        '+ ') or line.startswith('- ')]

    # Return the list of differences as a single string
    return '\n'.join(diff)


def run_gnatprove(file_location: str):
    """
    Executes the 'alr gnatprove' command on a specific directory or project location using a pseudo-terminal (pty)
    to capture all types of output. The function changes the working directory to 'file_location' before executing
    the 'alr gnatprove' command.

    Args:
        file_location (str): The absolute path of the directory where the 'alr' session is initialized or the project root.

    Returns:
        tuple: A tuple containing the captured output (stdout and stderr) as a string and the return code of the process.

    Note:
        This function assumes that 'alr gnatprove' is properly configured and can be executed within the specified
        'file_location'. Make sure the 'file_location' points to the directory where the 'alr' session is initialized.
    """
    
    # Create a pseudo-terminal to capture all output
    master_fd, slave_fd = pty.openpty()

    try:
        # Change the current working directory to the file_location
        os.chdir(file_location)

        # Start the subprocess with the pty slave as its stdin, stdout, and stderr
        # Removed 'file_location' from the command since we're already in the directory
        process = subprocess.Popen(
            ["alr", "gnatprove"],
            stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
            text=True, bufsize=0
        )

        # Close the slave FD because we are not going to write to it
        os.close(slave_fd)

        # Read output from the process through the master FD
        output = []
        while True:
            ready, _, _ = select.select([master_fd], [], [], 0.1)
            if ready:
                data = os.read(master_fd, 1024)
                # Break if read is empty (EOF)
                if not data:
                    break
                output.append(data.decode())
            elif process.poll() is not None:
                # If select timed out and process is done, we are finished
                break

        # Make sure the process has terminated
        process.wait()

        # Output everything we've captured from the pty
        complete_output = ''.join(output)

        if process.returncode == 0:
            print("alr gnatprove ran successfully.")
        else:
            print(f"alr gnatprove exited with code {process.returncode}.")

        return complete_output, process.returncode

    except Exception as e:
        print(f"An exception occurred: {e}")
        raise

    finally:
        # Close the master FD
        os.close(master_fd)

