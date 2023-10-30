import subprocess

def run_gnatprove(file_location):
    """
    
    
    """
    try:
        result = subprocess.run(["alr", "gnatprove", file_location], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"
