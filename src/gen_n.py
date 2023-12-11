from src.util import *
from assistant_manager import openai_assistant


class gen_1:
    """
    This class runs the benchmark, generating only a SINGLE solution per problem. 
    
    Args:
            instructions (str): Instructions detailing the purpose of the Assistant. Example: "You are a programmer. Fix the sent python code so that it runs correctly"
            benchmark_dir (str): The directory containing the benchmark files.
    """    
    
    def __init__(self, instructions: str, benchmark_dir: str):
        
        # Initialize the assistant
        self.instructions = instructions
        
        # Retrieve the benchmark files
        self.benchmark_files = retrieve_filenames_from_dir(benchmark_dir)
        
    
    def run_benchmark(self):
        
        # Create the assistant
        assistant = openai_assistant(self.instructions)
        
        # For each file in the benchmark, run gnatprove and extract the medium and line of code
        
        
        # For item in benchmark, get the associated medium and concatenate to the code example, then run assistant.create_message(item)
        
        # assistant.retrieve_messages()
    
    
    
    
    
        
    



    
    
    
    