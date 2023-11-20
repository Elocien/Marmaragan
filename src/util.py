from langchain.prompts import load_prompt
import json
import os
import subprocess
import re
import pty
import select


import os
import json


def ada_to_json(source_file: str, prompt_text: str, *context_files) -> None:
    """
    Takes an .adb file as input and optionally associated .ads files to generate an LLM prompt 
    which is then written to a JSON file. Each code block from the .adb and .ads files is individually
    delimited with markers for ADA code.
    
    Args:
        source_file (str): The path to the source file.
        prompt_text (str): The text to be used as part of the prompt.
        *context_files: Variable number of paths to the context files.
        
    Raises:
        ValueError: If the provided source_file or any of the context files do not have an .adb or .ads extension.
    """
    valid_extensions = ('.adb', '.ads')

    # Function to read file and enclose content in '''ada
    def read_and_delimit_ada_code(file_path: str):
        if os.path.splitext(file_path)[1] not in valid_extensions:
            raise ValueError(
                f"Invalid file extension for file: {file_path}. File must have .adb or .ads extension.")
        with open(file_path, 'r') as file:
            return f"'''ada\n{file.read()}\n'''\n"

    # Initialize the template content with the prompt text and process all files
    template_content = f"{prompt_text}\n\n"
    files_to_process = [source_file] + list(context_files)
    for file in files_to_process:
        template_content += read_and_delimit_ada_code(file)

    # Construct the data dictionary
    data = {
        "_type": "prompt",
        "input_variables": [],
        "template": template_content.strip()  # Remove the last newline
    }

    # Write the data dictionary to a JSON file
    with open('prompt.json', 'w') as f:
        json.dump(data, f, indent=4)






def get_prompt(file_name : os.path) -> str:
    """
    Loads the prompt which is passed to the LLM from a JSON file. 
    """
    return load_prompt(file_name).format()



def sanitize_output(api_output: str) -> str | None:
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



def overwrite_destination_file_with_string(file_path : os.path, content : str) -> None:
    '''
    Overwrites the input ada file with new content (in this case LLM output)
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError:
        print(f"An error occurred while trying to overwrite the file {file_path}.")




def compare_files_and_check(original_file_path, modified_file_path) -> bool:
    """
    Compare two files to determine if changes have been made to the original file,
    except for:
    - A SINGLE block of new lines added at one place in the file, and
    - The removal of comments (for the case where a comment indicates a location)

    Parameters:
    - original_file_path: path to the original file
    - modified_file_path: path to the modified file

    Returns:
    - True if the files are effectively the same (disregarding a single block of new lines and comment removal)
    - False if there are other changes in the modified file
    """

    with open(original_file_path, 'r') as file:
        original_lines = file.readlines()

    with open(modified_file_path, 'r') as file:
        modified_lines = file.readlines()

    # Strip comments
    original_lines = [line.split('--')[0].strip() for line in original_lines]
    modified_lines = [line.split('--')[0].strip() for line in modified_lines]

    # Strip whitespace
    original_lines = [line for line in original_lines if line]
    modified_lines = [line for line in modified_lines if line]

    # Initialise Index
    orig_index = 0
    mod_index = 0
    
    # Flag to track if a block of new lines has been found, this may only occur once
    block_of_new_lines_found = False

    while orig_index < len(original_lines) and mod_index < len(modified_lines):
        if original_lines[orig_index] == modified_lines[mod_index]:
            orig_index += 1
            mod_index += 1
        elif not block_of_new_lines_found and modified_lines[mod_index] not in original_lines:
            # We've encountered a new line; now check for a contiguous block of new lines
            while mod_index + 1 < len(modified_lines) and modified_lines[mod_index + 1] not in original_lines:
                mod_index += 1
            mod_index += 1  # Move past the last line of the new block
            block_of_new_lines_found = True
        else:
            # If we've already found a block of new lines or the line doesn't match and isn't a contiguous block, return False
            return False

    # If we've reached the end of the original file without finding multiple discrepancies, return True
    # This means any remaining lines in the modified file are additions, which is allowed only if no block was found before
    return orig_index == len(original_lines) and (not block_of_new_lines_found or mod_index == len(modified_lines))



def run_gnatprove(file_location: str) -> (str, str):
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
