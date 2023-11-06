from langchain.prompts import load_prompt
import json
import os
import subprocess
import re
import shutil
import pty
import tty
import select




def ada_to_json(input_file : os.path, prompt_text : str):
    """
    Takes an .adb file as input in order to generate an LLM prompt which is written to a JSON file
    """
    valid_extensions = ('.adb', '.ads')
    
    # TODO: Pass in .ads file, as well as .adb
    
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


def get_prompt(file_name : os.path):
    """
    Loads the prompt which is passed to the LLM from a JSON file. 
    """
    prompt = load_prompt(file_name)
    
    return prompt.format()



def sanitize_output(api_output: str):
    """
    Extracts and returns Ada code blocks from the given GPT-4 API output.
    """
    # Define the pattern to capture the code block between '''ada and '''
    pattern = re.compile(r"'''ada(.*?)'''", re.DOTALL)

    # Search for the pattern in the input string
    match = pattern.search(api_output)

    # If a match is found, return the code block without the delimiters
    if match:
        return match.group(1).strip()

    # If no match is found, return an empty string or None
    return None


def overwrite_ada_file_with_string(file_path : os.path, new_string : str):
    '''
    Overwrites the input ada file with new content (in this case LLM output)
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(new_string)
    except IOError:
        print(f"An error occurred while trying to overwrite the file {file_path}.")



def overwrite_file(source_path, destination_path):
    """
    Overwrites the content of the destination file with the content of the source file.
    """
    try:
        shutil.copyfile(source_path, destination_path)
        print(f"The file {destination_path} has been successfully overwritten with the content of {source_path}.")
    except IOError as e:
        print(f"An error occurred: {e.strerror}")


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
        print(complete_output)

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

