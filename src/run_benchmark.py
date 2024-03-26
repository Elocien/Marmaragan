from time import sleep
from src.util import *
import shutil
import logging
import time
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage, AIMessage
from langchain_core.outputs import ChatResult
from typing import List, Tuple




class run_benchmark:
    """
    This class is used to run the benchmark. It contains methods to run the benchmark with different configurations and to generate the results. 
    All results are logged to the benchmark_run.log file.
    
    Args:
            system_message (str): Instructions detailing the purpose of the Assistant. Example: "You are a programmer. Fix the sent python code so that it runs correctly"
            benchmark_dir (str): The directory containing the benchmark files.
            gpt_model (str): The GPT model to use. Choice of "gpt-3.5-turbo-1106", "gpt-4-0125-preview" or "gpt-4-0613"
            benchmark_program_indices (List[int]): A list of the indices of the programs in the benchmark to run. Default is all programs in the benchmark
    """    
    
    def __init__(self, system_message: str, benchmark_dir: str, gpt_model: str, n_solutions: int, benchmark_program_indices: List[int] = list(range(1, 17))):
        
        # Set the system message and gpt model
        self.system_message = system_message
        self.gpt_model = gpt_model
        self.n_solutions = n_solutions
        
        # Retrieve the benchmark files
        self.benchmark_txt_files = retrieve_benchmark_files(benchmark_dir, benchmark_program_indices)
        print(self.benchmark_txt_files)
        
        
        # Name of the temporary directory to store the spark files
        self.tmp_benchmark_dir = "tmp_benchmark_dir"


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
        
        
        self.start_time = None;
        self.end_time = None;
        






    def init_run(self, prompt_type: str) -> List[Tuple[str, str]]:
        """
        This class initialises the run and creates the temporary files for the benchmark.
        
        Args:
            prompt_type (str): The type of prompting technique to use. Either "chain_of_thoughts" or "gnatprove_pre_compile"
        
        Returns:
            List[Tuple[str, str]]: A list of tuples containing the temporary filepath of the gpr files and the permanent txt files.
        
        """
        
        # self.logger.info(
        #     f"New Run \nGPT Model: {gpt_model} \nInstructions: \n{instructions} \n-----------------------------------\n\n")
        
        
        # Start timing
        self.start_time = time.time()
        print("Starting Benchmark Run:\n")
        
        # Pretty print the benchmark files
        benchmark_programs = [file.split("/")[-1] for file in self.benchmark_txt_files]
        nl = '\n'
        
        
        self.logger.info(f"""
\n\n\n
--------------------------
Starting new Benchmark Run
--------------------------
Model: {self.gpt_model} \n
Programs: \n{nl.join(map(str, benchmark_programs))} \n
n: {self.n_solutions}
Prompt Type: {prompt_type} \n
System Message: \n{self.system_message}
--------------------------
\n\n\n
                         """)
        
        
    # For each file in the benchmark, run gnatprove and extract the medium and line of code
        
        
        # Array of tuples, containing the results, of the form:
        # [(program-name, gnatprove-successful-compilation, medium-free)]
        self.results = []
        
        # Remove dir if it exists 
        try:
            shutil.rmtree(self.tmp_benchmark_dir)
            sleep(1)
        except Exception:
            pass
        
        # generate temporary directory for the spark files
        os.mkdir(self.tmp_benchmark_dir)
        
        # Array of containing the temporary filepath of the gpr files and the permanent txt files, as a tuple
        benchmark_files = []
        
        # Iterate over each file in the benchmark and generate the files in the spark_benchmark directory
        for benchmark_file_path in self.benchmark_txt_files:
            gpr_file_path = generate_spark_files(benchmark_file_path, self.tmp_benchmark_dir)
            benchmark_files.append((gpr_file_path, benchmark_file_path))
            
        
        return benchmark_files
        
    
    def end_run(self, results_array: List[Tuple[bool, bool]]) -> None:
        
        successes = 0
        failures = 0
        
        # Compile a string of the results_array
        summary_array = []
        for project, compilation_successful, no_mediums in results_array:
            if no_mediums:
                summary_array.append(f"Success: {project}")
                successes += 1
            else:
                summary_array.append(f"Failure: {project}")
                failures += 1
                
        
        summary_string = "\n".join(summary_array)
        
        # Compile the totals of the results_array
        
        
        # End timing and log
        self.end_time = time.time()  # End timing
        duration = self.end_time - self.start_time

        self.logger.info(f"""
\n\n\n
--------------------------
End of Benchmark Run
--------------------------
{summary_string}
Time taken: {duration} \n
Summary of results:
{successes} / {failures}
--------------------------
\n\n\n
                         """)
    



    def invoke_llm(self, prompt: str) -> List[str]:
        """
        This class invokes the LLM to generate n solutions for a given prompt. If n is 1, it returns a single solution
        """
        
        # List of solutions
        solutions = []
        
        # Initialise the chat model
        chat_model = ChatOpenAI(
            model_name=self.gpt_model,
            temperature=1.0,
            n=self.n_solutions
        )
        
        # Create a human message
        message = HumanMessage(content=prompt)
        
        response = chat_model._generate([message])  # Generate responses
        # Check if the response is a ChatResult object
        assert isinstance(response, ChatResult)
        assert len(response.generations) == self.n_solutions  # Check if 5 responses are generated
        for generation in response.generations:
            assert isinstance(generation.message, BaseMessage)
            assert isinstance(generation.message.content, str)
            solutions.append(generation.message.content)

        
        
        return solutions
    
    
    def extract_code_and_write_file(self, llm_response: str, gpr_file_path: str, response_number_counter: int) -> bool:
        """
        Extracts the fixed code from the LLM response and writes it to a file in the benchmark directory.
        Returns True if the extraction and writing is successful, False otherwise.
        """
        # Init compile success flag
        compile_success = True

        llm_code = ""
        adb_file_path = ""

        # Extract the code from the response
        try:
            llm_code = extract_code_from_response(llm_response)
        except ValueError as e:
            compile_success = False
            self.logger.error(
                f"\n-----------------------------------\nError extracting code from response number: {gpr_file_path.split('/')[-1]}:{response_number_counter}\nCode: {llm_response}\n-----------------------------------\n\n")

        if llm_code not in ["", None]:

            # Extract the filename from the response
            try:
                adb_filename = extract_filename_from_response(
                    llm_code)

                # Convert filename to lowercase and add .adb extension
                filename_with_extension = adb_filename.lower() + ".adb"

                project_dir = "/".join(gpr_file_path.split("/")[:-1])
                adb_file_path = project_dir + "/" + filename_with_extension

                # Overwrite the destination file with the response code
                overwrite_destination_file_with_string(
                    adb_file_path, llm_code)

            except ValueError as e:
                compile_success = False
                self.logger.error(
                    f"\n-----------------------------------\n\nError extracting filename from response: {gpr_file_path.split('/')[-1]}:{response_number_counter}\nCode: {llm_code}\n-----------------------------------\n\n")

        return compile_success

        



    
    
    def gnatprove_pre_compile(self) -> None:
        """
        This class runs the benchmark, running gnatprove to identify any mediums and including this information in the prompt
        """
        
        # Initialise the run and retrieve the benchmark files
        benchmark_files = self.init_run("With Gnatprove mediums in Prompt")
        
        # f string newline fix   
        nl = "\n"
        
        
    # Iterate over each project in the benchmark
        for benchmark_file_path in benchmark_files:
            
            gpr_file_path = benchmark_file_path[0]
            

        # Run gnatprove on the project
            output = run_gnatprove(gpr_file_path)
            mediums = parse_gnatprove_output(output)
            
            project_dir = "/".join(gpr_file_path.split("/")[:-1])
            

            # Compile the lines of code, which are referenced in the mediums
            # E.g. for medium: swap_ranges_p.adb:17:13: overflow check might fail, extract line 17 from file swap_ranges_p.adb
            medium_code_reference = []
            
            for medium in mediums:
                medium_code_reference.append(
                    (extract_line_of_code_from_file(medium, project_dir), medium[1]))
            
            
            # retrieve the benchmark txt file
            benchmark_file = open(benchmark_file_path[1], "r")
            
            # Format medium code reference
            medium_code_reference = "\n".join(f"Line: {line},\n Explanation: {explanation}\n" for line, explanation in medium_code_reference)
            
        
        
        
        
        
        # Format prompt
            prompt = f"""\
The following code is a Spark2014/ADA project.\n\n
{benchmark_file.read()}


Here are the current mediums being thrown by gnatprove, in the form of the line referenced as the cause and an explaination:\n\n
{medium_code_reference}

Return the fixed code for the first implementation file, delimiting with 
```ada

code here

```
"""

        
    # Invoke the LLM to generate the response
            print(benchmark_file_path[1])   
            llm_responses = self.invoke_llm(prompt)
            
            # Used to index the differnt solutions in the log
            response_number_counter = 0
            
            for llm_response in llm_responses:
                
                response_number_counter += 1
                
                
        # Extract the fixed code and write to file in the benchmark_dir
                # Init compile success flag
                compile_success = True

                llm_code = ""
                adb_file_path = ""

                # Extract the code from the response
                try:
                    llm_code = extract_code_from_response(llm_response)
                except ValueError as e:
                    compile_success = False
                    self.logger.error(
                        f"\n-----------------------------------\nError extracting code from response number: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nCode: {llm_response}\n-----------------------------------\n\n")

                if llm_code not in ["", None]:

                    # Extract the filename from the response
                    try:
                        adb_filename = extract_filename_from_response(
                            llm_code)

                        # Convert filename to lowercase and add .adb extension
                        filename_with_extension = adb_filename.lower() + ".adb"

                        project_dir = "/".join(gpr_file_path.split("/")[:-1])
                        adb_file_path = project_dir + "/" + filename_with_extension

                        # Overwrite the destination file with the response code
                        overwrite_destination_file_with_string(
                            adb_file_path, llm_code)

                    except ValueError as e:
                        compile_success = False
                        self.logger.error(
                            f"\n-----------------------------------\n\nError extracting filename from response: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nCode: {llm_code}\n-----------------------------------\n\n")


            
            
            # Three cases:
            # 1. Code was successfully extracted and gnatprove made it to stage 2. of compilation
            # 2. Code was successfully extracted but gnatprove did not make it to stage 2. of compilation
            # 3. Code was not successfully extracted and gnatprove did not run
                
                
                if compile_success == True:

                    # Run gnatprove on the project
                    gnatprove_output = run_gnatprove(gpr_file_path)
                    gnatprove_successful_compilation = is_compilation_successful(
                        gnatprove_output)

                    # Case 1
                    # Code was successfully extracted and gnatprove made it to stage 2. of compilation
                    if gnatprove_successful_compilation:

                        # Parse the new mediums
                        new_mediums = parse_gnatprove_output(gnatprove_output)

                        self.results.append((gpr_file_path.split(
                            "/")[-1], compile_success, len(new_mediums) == 0))
                        
                        
                        # Logging
                        self.logger.info(
                            f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter} \n\nResponse: \n{nl.join(compute_diff(retrieve_package_body(benchmark_file_path[1]), llm_code))}\n\nNew Mediums: \n{new_mediums}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")

                    # Case 2
                    # Code was successfully extracted but gnatprove did not make it to stage 2. of compilation
                    else:
                        self.results.append(
                            (gpr_file_path.split("/")[-1], compile_success, False))

                        # Logging
                        self.logger.info(
                            f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter} \n\nResponse: \n{nl.join(compute_diff(retrieve_package_body(benchmark_file_path[1]), llm_code))}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")

                # Case 3
                #  Code was not successfully extracted and gnatprove did not run
                else:

                    self.results.append(
                        (gpr_file_path.split("/")[-1], False, False))

                    # Logging
                    self.logger.info(
                        f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nError: GnatProve did not run. Either the filename or code could not be extracted from the response.\n\nResponse: \n{llm_code}\n-----------------------------------\n\n")

        # End the run and log summary
        self.end_run(self.results)







    
    
    
    
    def chain_of_thoughts(self) -> None:
        """
        This class runs the benchmark, using the chain of thoughts prompting technique
        """
        
        
        # Initialise the run and retrieve the benchmark files
        benchmark_files = self.init_run("Zero Shot Chain of Thoughts")
        
        
    # Iterate over each project in the benchmark
        for benchmark_file_path in benchmark_files:
            
            gpr_file_path = benchmark_file_path[0]
            
            # f string newline fix   
            nl = "\n"
            
            dependencies = retrieve_dependencies(benchmark_file_path[1])
            package_body = retrieve_package_body(benchmark_file_path[1])
            
            
            zero_shot_CoT_prompt = f"""\n
Try to solve the following problem logically and step by step. The final answer should then be delimited in the following way:

```ada

code here

```

The following are the specifications and dependencies of a Spark2014/ADA project:

{nl.join(dependencies)} \n

This is the package body (implementation):

{package_body} \n

Add a single 'pragma Loop_Invariant' statement to the package body, so that the code runs error and medium free. 
Do not modify the code in any other way. Return the entire implementation file with the single addition.

                    """
                    
            
    # Invoke the LLM to generate the response
            print(benchmark_file_path[1])   
            llm_responses = self.invoke_llm(zero_shot_CoT_prompt)
            
            # Used to index the differnt solutions in the log
            response_number_counter = 0
            
            for llm_response in llm_responses:
                
                response_number_counter += 1

        # Extract the fixed code and write to file in the benchmark_dir

                # Init compile success flag
                compile_success = True

                llm_code = ""
                adb_file_path = ""

                # Extract the code from the response
                try:
                    llm_code = extract_code_from_response(llm_response)
                except ValueError as e:
                    compile_success = False
                    self.logger.error(
                        f"\n-----------------------------------\nError extracting code from response number: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nCode: {llm_response}\n-----------------------------------\n\n")

                    
                if llm_code not in ["", None]:

                    # Extract the filename from the response
                    try:
                        adb_filename = extract_filename_from_response(
                            llm_code)

                        # Convert filename to lowercase and add .adb extension
                        filename_with_extension = adb_filename.lower() + ".adb"
                        
                        project_dir = "/".join(gpr_file_path.split("/")[:-1])
                        adb_file_path = project_dir + "/" + filename_with_extension
                        

                        # Overwrite the destination file with the response code
                        overwrite_destination_file_with_string(
                            adb_file_path, llm_code)

                    except ValueError as e:
                        compile_success = False
                        self.logger.error(
                            f"\n-----------------------------------\n\nError extracting filename from response: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nCode: {llm_code}\n-----------------------------------\n\n")

            
            
            # Three cases:
            # 1. Code was successfully extracted and gnatprove made it to stage 2. of compilation
            # 2. Code was successfully extracted but gnatprove did not make it to stage 2. of compilation
            # 3. Code was not successfully extracted and gnatprove did not run
                
                
                if compile_success == True:

                    # Run gnatprove on the project
                    gnatprove_output = run_gnatprove(gpr_file_path)
                    gnatprove_successful_compilation = is_compilation_successful(
                        gnatprove_output)

                    # Case 1
                    # Code was successfully extracted and gnatprove made it to stage 2. of compilation
                    if gnatprove_successful_compilation:

                        # Parse the new mediums
                        new_mediums = parse_gnatprove_output(gnatprove_output)

                        self.results.append((f"{gpr_file_path.split('/')[-1]} : attempt {response_number_counter}", compile_success, len(new_mediums) == 0))
                        
                        
                        # Logging
                        self.logger.info(
                            f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter} \n\nResponse: \n{nl.join(compute_diff(retrieve_package_body(benchmark_file_path[1]), llm_code))}\n\nNew Mediums: \n{new_mediums}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")

                    # Case 2
                    # Code was successfully extracted but gnatprove did not make it to stage 2. of compilation
                    else:
                        self.results.append(
                            (f"{gpr_file_path.split('/')[-1]} : attempt {response_number_counter}", compile_success, False))

                        # Logging
                        self.logger.info(
                            f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter} \n\nResponse: \n{nl.join(compute_diff(retrieve_package_body(benchmark_file_path[1]), llm_code))}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")

                # Case 3
                #  Code was not successfully extracted and gnatprove did not run
                else:

                    self.results.append(
                        (f"{gpr_file_path.split('/')[-1]} : attempt {response_number_counter}", False, False))

                    # Logging
                    self.logger.info(
                        f"Project: {gpr_file_path.split('/')[-1]} : attempt {response_number_counter}\nError: GnatProve did not run. Either the filename or code could not be extracted from the response.\n\nResponse: \n{llm_code}\n-----------------------------------\n\n")

        # End the run and log summary
        self.end_run(self.results)

                    

            
