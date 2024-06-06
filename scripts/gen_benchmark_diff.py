import os
from difflib import unified_diff


def calculate_diff_with_line_numbers(original_dir, modified_dir):
    differences = []

    if not os.path.exists(modified_dir):
        print("modified_dir does not exist.")
        return


    # Ensure the directories exist
    if not os.path.exists(original_dir):
        print("Original_dir does not exist.")
        return

    # Iterate over each file in the original directory
    for filename in os.listdir(original_dir):
        original_file_path = os.path.join(original_dir, filename)
        
        
        mod_filenames = [f for f in os.listdir(modified_dir) if f.startswith(filename.split('-', 1)[0])]
        for mod_filename in mod_filenames:
            modified_file_path = os.path.join(modified_dir, mod_filename)
            print(modified_file_path)
            # Rest of the code for comparing the original file to each modified file

            # Ensure the file exists in the modified directory
            if not os.path.exists(modified_file_path):
                print(f"File {filename} missing in modified directory.")
                continue

            with open(original_file_path, 'r') as original_file, open(modified_file_path, 'r') as modified_file:
                original_lines = original_file.readlines()
                modified_lines = modified_file.readlines()

                # Calculate the difference
                diff = list(unified_diff(original_lines, modified_lines,
                            fromfile='original', tofile='modified', lineterm=''))
                line_number = 0
                for line in diff:
                    if line.startswith('-') and not line.startswith('---'):
                        # Find the line number in the original file
                        for i, original_line in enumerate(original_lines, start=1):
                            if original_line.strip() == line[1:].strip() and i > line_number:
                                line_number = i
                                break
                        differences.append(
                            (filename, line_number, line[1:].strip()))

    return differences

