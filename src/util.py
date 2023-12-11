import textwrap
from openai import OpenAI
import os
import re



def overwrite_destination_file_with_string(file_path : os.path, content : str) -> None:
    '''
    Overwrites the input ada file with new content (in this case LLM output)
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError:
        print(f"An error occurred while trying to overwrite the file {file_path}.")




def compare_files_and_check(original_file_path: str, modified_file_path: str) -> bool:
    """
    Compare two files to determine if changes have been made to the original file,
    except for:
    - A SINGLE block of new lines added at one place in the file, and
    - The removal of comments (for the case where a comment indicates a location)

    Args:
        original_file_path (str): path to the original file
        modified_file_path (str): path to the modified file

    Returns:
        True: if the files are effectively the same (disregarding a single block of new lines and comment removal)
        False: if there are other changes in the modified file
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





def retrieve_filenames_from_dir(directory: str) -> list[str]:
    """
    Retrieve all filenames in the given directory, including those in subdirectories.
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list




def delete_all_assistants() -> None:
    """
    # Function to delete all assistants with the OpenAI API
    """
    
    # Initialize the OpenAI client
    client = OpenAI()
    
    # List all assistants
    list_of_assistants = client.beta.assistants.list(order="desc").data

    # Iterate over each assistant and delete them
    for assistant in list_of_assistants:
        print(f"Assistant id: {assistant.id}")
        # Delete the assistant
        response = client.beta.assistants.delete(assistant.id)
        print(response)
        
        
def generate_spark_files(file_path: str, directory_path: str) -> [str]:
    """
    This function takes a benchmark file and generates the corresponding spark files in the given directory.
    It also generates a gpr file for each project and returns a list of paths to the generated gpr files.
    
    Args:
        file_path (str): Path to the benchmark file
        directory_path (str): Path to the directory where the benchmark files will be generated
        
    Returns:
        List of paths to the generated gpr files
    """
    
    # List of file paths, used late to compile projects
    gpr_file_paths = []
    
    # Open the benchmark file
    with open(file_path, 'r') as file:
        input_text = file.read()
        
        # String containing name of subdir to create for a given benchmark file
        subdir_path = None

        # Split the complete text file from the benchmark into seperate spark files
        for section in input_text.split('-- start file '):
            
            # Check if the section is not empty
            if section.strip():  
                
                # Further split the section to separate the filename and code
                parts = section.split('\n', 1)
                filename = parts[0].strip()
                code = parts[1].split('-- end file', 1)[0].strip()
                
                if subdir_path is None:
                    
                    # Get the subdir path from the filename. The first piece of code in the benchmark file is
                    # always the name of the project
                    subdir_path = os.path.join(
                        directory_path, filename.split('.')[0])
                    os.mkdir(subdir_path)
                    
                    # Author: Emmanuel Debanne
                    # ---------------------------------------------------------------
                    gpr_file_name = f"{filename.split('.')[0]}.gpr"
                    
                    
                    # Generate project file 
                    with open(os.path.join(subdir_path, gpr_file_name), 'w') as file:
                        gpr_file_content = textwrap.dedent(
                            f"""\
                            project {filename} is
                                for Source_Dirs use (".");
                            end Group;
                            """
                        )
                    # ---------------------------------------------------------------
                        file.write(gpr_file_content)
                    
                    # Add project file to list of gpr files
                    gpr_file_paths.append(subdir_path)

                # Save the code to a file
                with open(os.path.join(subdir_path, filename), 'w') as file:
                    file.write(code)
        
        
        return gpr_file_paths
                    
    

