import subprocess
from time import sleep
from src.util import *
from src.assistant_manager import openai_assistant
from openai import OpenAI
import shutil
import asyncio



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
        
        benchmark_dir = "spark_benchmark"
        
        # Create the assistant
        # assistant = openai_assistant(self.instructions)
        
    # For each file in the benchmark, run gnatprove and extract the medium and line of code
        
        
        # Remove dir if it exists 
        try:
            shutil.rmtree(benchmark_dir)
            sleep(1)
        except Exception:
            pass
        
        # generate temporary directory for the spark files
        os.mkdir(benchmark_dir)
        
        benchmark_gpr_files = []
        
        # Iterate over each file in the benchmark and generate the files in the spark_benchmark directory
        for file_path in self.benchmark_files:
            gpr_file_path = generate_spark_files(file_path, benchmark_dir)
            benchmark_gpr_files.append(gpr_file_path)
        
    # For item in benchmark, get the associated medium and concatenate to the code example, then run assistant.create_message(item)
        
        for project in benchmark_gpr_files:
            # Run gnatprove on the project
            mediums = asyncio.run(run_gnatprove(project))
            
            
            # Iterate over each medium and extract line of code and error message
            

        
    # Retrieve the messages from the assistant
        # messages = assistant.retrieve_messages()
        
    # For each message, extract the fixed code and write to file in the benchmark_dir
    
    # Run gnatprove on the fixed code and extract any mediums 
    
    # Delete the assistant
        # assistant.delete_assistant()
        
    # Delete the temporary directory
        # shutil.rmtree(benchmark_dir)

    
    
    
    
    
        
    



    
    
    
    