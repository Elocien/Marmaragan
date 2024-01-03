from time import sleep
from src.util import *
from src.assistant_manager import openai_assistant
import shutil
import asyncio
import textwrap
import logging



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
        
        # Deletes all current assistants
        # delete_all_assistants()
        
        # Setup Logger
        self.logger = logging.getLogger('gen_1')
        self.logger.setLevel(logging.INFO)

        # Create a file handler which logs even debug messages
        fh = logging.FileHandler('benchmark_run.log')
        fh.setLevel(logging.INFO)

        # Create a formatter and set the formatter for the handler.
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(fh)


        
    
    def run_benchmark(self):
        
        benchmark_dir = "spark_benchmark"
        
        # Create the assistant
        assistant = openai_assistant(self.instructions)
        
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
        for benchmark_file_path in self.benchmark_files:
            gpr_file_path = generate_spark_files(benchmark_file_path, benchmark_dir)
            benchmark_gpr_files.append(gpr_file_path)
            

        # Run gnatprove on the project
            mediums = asyncio.run(run_gnatprove(gpr_file_path))
            
            project_dir = "/".join(gpr_file_path.split("/")[:-1])
            

            # Compile the lines of code, which are referenced in the mediums
            # E.g. for medium: swap_ranges_p.adb:17:13: overflow check might fail, extract line 17 from file swap_ranges_p.adb
            medium_code_reference = []
            
            for medium in mediums:
                medium_code_reference.append(
                    (extract_line_of_code_from_file(medium, project_dir), medium[1]))
            
            
            # retrieve the benchmark txt file
            benchmark_file = open(benchmark_file_path, "r")
            
            # Format medium code reference
            medium_code_reference = "\n".join(f"Line: {line},\n Explanation: {explanation}\n" for line, explanation in medium_code_reference)
            
        # Format prompt
            prompt = f"""\
                The following code is a Spark2014/ADA project.\n\n
                {benchmark_file.read()}
                
                
                Here are the current mediums being thrown by gnatprove, in the form of the line referenced as the cause and an explaination:\n\n
                {medium_code_reference}
                
                Return the fixed code for the first implementation file, delimiting with ```ada\n and \n```
                """
           
           
            thread_id = assistant.create_message(textwrap.dedent(prompt))


        
    # Retrieve the messages from the assistant
            message = assistant.retrieve_messages(thread_id)
            message_content = message[0].content[0].text.value
            
        
    # Extract the fixed code and write to file in the benchmark_dir

            api_response_code = ""
            
            # Extract the code from the response
            try:
                api_response_code = extract_code_from_response(message_content)
            except ValueError as e:
                self.logger.error(f"Error extracting code from response: {e}")


            adb_filename = ""

            # Extract the filename from the response
            try:
                adb_filename = extract_filename_from_response(api_response_code)
            except ValueError as e:
                self.logger.error(f"Error extracting filename from response code: {e}")

            
            # Convert filename to lowercase and add .adb extension
            filename_with_extension = adb_filename.lower() + ".adb"
            
            adb_file_path = project_dir + "/" + filename_with_extension
            
            # Overwrite the destination file with the response code
            overwrite_destination_file_with_string(
                adb_file_path, api_response_code)
            
            
    
        # Run gnatprove on the fixed code and extract any mediums 
            
            # Run gnatprove on the project
            new_mediums = asyncio.run(run_gnatprove(gpr_file_path))
            
            
        # Logging
            self.logger.info(
                f"Project: {gpr_file_path.split('/')[-1]} | Initial Mediums: {mediums} | Prompt: \n{prompt} | Response: \n{api_response_code} \n| New Mediums: \n{new_mediums} \n -----------------------------------\n\n")
            
            


    
    # Delete the assistant
        assistant.delete_assistant()
        
        
    # Delete the temporary directory
        # shutil.rmtree(benchmark_dir)

    
    
    
    
    
        
    



    
    
    
    