from time import sleep
from src.util import *
import shutil
import logging
import time
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, BaseMessage
from langchain_core.outputs import ChatResult
from typing import List, Tuple




class run_benchmark:
    """
    This class is used to run the benchmark. It contains methods to run the benchmark with different configurations and to generate the results. 
    All results are logged to the benchmark_run.log file.
    
    Args:
            system_message (str): Instructions detailing the context for the language model
            benchmark_dir (str): The directory containing the benchmark files.
            gpt_model (str): The GPT model to use. Choice of "gpt-3.5-turbo-1106", "gpt-4-0125-preview" or "gpt-4-0613"
            benchmark_program_indices (List[int]): A list of the indices of the programs in the benchmark to run. Default is all programs in the benchmark
    """    
    
    def __init__(self, system_message: str, prompt: str, benchmark_dir: str, gpt_model: str, n_solutions: int, retries: int, with_medium_in_prompt: bool, benchmark_program_indices: List[int] = list(range(1, 17))):
        
        # Set the system message and gpt model
        self.system_message = system_message
        self.prompt = prompt
        self.benchmark_dir = benchmark_dir
        self.gpt_model = gpt_model
        self.n_solutions = n_solutions
        self.retries = retries
        self.with_medium_in_prompt = with_medium_in_prompt
        
        
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
        
        # f string newline fix
        self.nl = "\n"
        


    
    def run(self) -> None:
        """
        This class runs the benchmark
        """
        
        
        # Initialise the run and retrieve the benchmark files
        benchmark_files = self.init_run()
        
        
    # Iterate over each project in the benchmark
        for benchmark_file_path in benchmark_files:
            
            gpr_file_path = benchmark_file_path[0]
            
            # Get dependencies and format as a string, get package_body
            dependencies = self.nl.join(retrieve_dependencies(benchmark_file_path[1]))
            package_body = retrieve_package_body(benchmark_file_path[1])
            
            # Format the prompt
            prompt = self.prompt.format(dependencies=dependencies, package_body=package_body)
            
            # If mediums are enabled, run gnatprove, extract the mediums and add them to the prompt
            if self.with_medium_in_prompt:
                
                # Update the prompt, by appending the mediums from the gnatprove 
                prompt = self.extract_mediums(gpr_file_path, prompt)
            

            # Dict which keeps track of gnatprove output of each generation. 
            # Key is the response number, value is a tuple containing the llm generated code and gnatprove output
            self.gnatprove_output_dict = {}
                    
            
    # Invoke the LLM to generate the response
            print(benchmark_file_path[1])   
            llm_responses = self.invoke_llm(prompt)
            
            # Used to index the differnt solutions in the log
            response_number_counter = 0
            
            # Used to index the number of retries
            retry_counter = 0
            
            
    # For each response, extract the fixed code and write to file in the benchmark_dir
            for llm_response in llm_responses:
                
                response_number_counter += 1
                
                original_package_body = retrieve_package_body(benchmark_file_path[1])
                
                # Extract the fixed code, compile and log the results. This returns a tuple indicating if a solution was found and if any mediums can be included in the retry.
                # If the code couldn't be extracted, or the filename couldn't be extracted, then solution_found_flag[1] is False
                solution_found_flag, gnatprove_output_flag = self.extract_compile_and_log(
                    llm_response, gpr_file_path, benchmark_file_path[1], response_number_counter, retry_counter, original_package_body)
                
                if solution_found_flag:
                    break
            
        
    # If retries are enabled, and no solution was found, retry with error message
            while not solution_found_flag and self.retries > 0:
                
                retry_counter += 1
                
                # Reset the prompt
                prompt = ""
                
                if gnatprove_output_flag:
                    
                    llm_response, gnatprove_output = self.gnatprove_output_dict[response_number_counter]
                    
                    # Add the LLM generated, broken package body to the prompt
                    prompt = self.prompt.format(
                        dependencies=dependencies, package_body=llm_response)
                    
                    # If mediums are enabled, run gnatprove, extract the mediums and add them to the prompt
                    if self.with_medium_in_prompt:

                        # Update the prompt, by appending the mediums from the gnatprove
                        prompt = self.extract_mediums(gpr_file_path, prompt)

                else:
                    # Same prompt as in the initial run
                    prompt = self.prompt.format(dependencies=dependencies, package_body=package_body)
                
                
                # Invoke the LLM to generate the response
                llm_responses = self.invoke_llm(prompt)
                
                # Reset counter
                response_number_counter = 0
        
                for llm_response in llm_responses:
                
                    response_number_counter += 1
                    
                    original_package_body = retrieve_package_body(benchmark_file_path[1])
                    
                    
                    solution_found_flag = self.extract_compile_and_log(
                        llm_response, gpr_file_path, benchmark_file_path[1], response_number_counter, retry_counter, original_package_body)
                    
                    if solution_found_flag[0]:
                        break   
        
        # End the run and log summary
        self.end_run(self.results)





    def init_run(self) -> List[Tuple[str, str]]:
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
        
        
        self.logger.info(f"""
\n\n\n
--------------------------
Starting new Benchmark Run
--------------------------
Model: {self.gpt_model} \n
Benchmark: {self.benchmark_dir} \n
Programs: \n{self.nl.join(map(str, benchmark_programs))} \n
n: {self.n_solutions}
Retries: {self.retries}
With Mediums in Prompt: {self.with_medium_in_prompt}\n
System Message: \n{self.system_message}
--------------------------
Prompt: \n{self.prompt}\n
--------------------------
\n\n\n
                         """)
        
        if self.with_medium_in_prompt:
            self.logger.info("""*** The prompt will include individually extracted mediums from the gnatprove output ***""")
        
        
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
        """
        This class ends the run by sumarrising results in the log
        
        Args:
            results_array (List[Tuple[bool, bool]]): A list of tuples containing the results of the form [(program-name, gnatprove-successful-compilation, medium-free)]
        
        Returns:
            None
        """
        
        successes = 0
        total = 0
        
        # Compile a string of the results_array
        summary_array = []
        for project, compilation_successful, no_mediums in results_array:
            if no_mediums:
                summary_array.append(f"Success: {project}")
                successes += 1
                total += 1
            else:
                summary_array.append(f"Failure: {project}")
                total += 1
                
        
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
{successes} / {total}
--------------------------
\n\n\n
                         """)
    



    def invoke_llm(self, prompt: str) -> List[str]:
        """
        This class invokes the LLM to generate n solutions for a given prompt. If n is 1, it returns a single solution
        
        Args:
            prompt (str): The prompt to send to the LLM
            
        Returns:
            List[str]: A list of strings containing each of the responses
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
        
        # Generate responses
        response = chat_model._generate([message]) 
        
        # Check if the response is a ChatResult object
        assert isinstance(response, ChatResult)
        assert len(response.generations) == self.n_solutions  # Check if correct number responses are generated
        for generation in response.generations:
            assert isinstance(generation.message, BaseMessage)
            assert isinstance(generation.message.content, str)
            solutions.append(generation.message.content)

        
        
        return solutions

    def extract_compile_and_log(self, llm_response: str, gpr_file_path: str, benchmark_file_name: str, response_number_counter: int, retry_counter: int, original_package_body: str) -> Tuple[bool, bool]:
        """
        This function extracts the code from the response, extracts the filepath and then overwrites the file in the temporary benchmark folder. 
        It then runs gnatprove on the project and logs the results. It returns a tuple indicating if a solution was found and if any mediums can be included in the retry.
        
        Args:
            llm_response (str): The response from the LLM
            gpr_file_path (str): The path to the gpr file
            benchmark_file_name (str): The name of the benchmark file
            response_number_counter (int): The index used to track the current llm response
            retry_counter (int): The index used to track the current retry number
            original_package_body (str): The original package body
        
        Returns:
            Tuple[bool, bool]: A tuple containing two boolean values. The first indicates if a solution was found. The second indicates if gnatprove output exists.
        """

        
        # Init variables
        project_name = gpr_file_path.split('/')[-1]
        compile_success = True
        llm_code = ""
        adb_file_path = ""

        # Extract the code from the response
        try:
            llm_code = extract_code_from_response(llm_response)

        # If the code cannot be extracted, set the compile success flag to False and log the error
        except ValueError as e:
            compile_success = False
            self.logger.error(
                f"\n-----------------------------------\nError extracting code from response number: {project_name} - benchmark No.: {benchmark_file_name} - attempt: {response_number_counter} - retry: {retry_counter}\nCode: {llm_response}\n-----------------------------------\n\n")

        # If code is not empty, extract the filename
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

            # If the filename cannot be extracted, set the compile success flag to False and log the error
            except ValueError as e:
                compile_success = False
                self.logger.error(
                    f"\n-----------------------------------\n\nError extracting filename from response: {project_name} - benchmark No.: {benchmark_file_name} - attempt: {response_number_counter} - retry: {retry_counter}\nCode: {llm_code}\n-----------------------------------\n\n")

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

                self.results.append(
                    (f"{project_name} - attempt: {response_number_counter} - retry: {retry_counter}", compile_success, len(new_mediums) == 0))

                # Logging
                self.logger.info(
                    f"Project: {project_name} - benchmark No.: {benchmark_file_name} - attempt: {response_number_counter} - retry: {retry_counter} \n\nResponse: \n{self.nl.join(compute_diff(original_package_body, llm_code))}\n\nNew Mediums: \n{new_mediums}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")

                # If the solution was medium free, break the loop
                if len(new_mediums) == 0:

                    # Log that a solution was found
                    self.logger.info(
                        f"Solution found for {project_name} - attempt: {response_number_counter} - retry: {retry_counter}\n\n")

                    return True, False
                
                # If not, continue
                else:
                    # Add the llm generated code and gnatprove output to the dictionary
                    self.gnatprove_output_dict[response_number_counter] = llm_code, gnatprove_output

                    return False, True
                    

            # Case 2
            # Code was successfully extracted but gnatprove did not make it to stage 2. of compilation
            else:
                self.results.append(
                    (f"{project_name} - attempt: {response_number_counter} - retry: {retry_counter}", compile_success, False))

                # Logging
                self.logger.info(
                    f"Project: {project_name} - benchmark No.: {benchmark_file_name} - attempt: {response_number_counter} - retry: {retry_counter} \n\nResponse: \n{self.nl.join(compute_diff(original_package_body, llm_code))}\n\nGnatprove Output: \n{gnatprove_output} \n-----------------------------------\n\n")
                
                # Add the llm generated code and gnatprove output to the dictionary
                self.gnatprove_output_dict[response_number_counter] = llm_code, gnatprove_output
                
                return False, True

        # Case 3
        #  Code was not successfully extracted and gnatprove did not run
        else:

            self.results.append(
                (f"{project_name} - attempt: {response_number_counter} - retry: {retry_counter}", False, False))

            # Logging
            self.logger.info(
                f"Project: {project_name} - benchmark No.: {benchmark_file_name} - attempt: {response_number_counter} - retry: {retry_counter}\nError: GnatProve did not run. Either the filename or code could not be extracted from the response.\n\nResponse: \n{llm_code}\n-----------------------------------\n\n")

            return False, False




            
    def extract_mediums(self, gpr_file_path: str, prompt: str) -> str:
        """
        Given a gpr file path and the prompt, this function runs gnatprove on the project and extracts the mediums from the output. 
        It then formats the mediums as a string and appends them to the prompt.
        
        Args:
            gpr_file_path (str): The path to the gpr file
            prompt (str): The prompt to send to the LLM
        
        Returns:
            str: A string containing the formatted_promt, with mediums appended
        
        """
    
        # Run gnatprove on the project
        output = run_gnatprove(gpr_file_path)
        
        # Returns list of Tuples
        medium_tuple = parse_gnatprove_output(output)

        project_dir = "/".join(gpr_file_path.split("/")[:-1])

        # Compile the lines of code, which are referenced in the mediums
        # E.g. for medium: swap_ranges_p.adb:17:13: overflow check might fail, extract line 17 from file swap_ranges_p.adb
        medium_code_reference = []

        for medium in medium_tuple:
            medium_code_reference.append(
                (extract_line_of_code_from_file(medium, project_dir), medium[1]))

        # Format medium code reference
        medium_code_reference = "\n\n".join(f"Line: {line},\nExplanation: {explanation}\n" for line, explanation in medium_code_reference)
        
        prompt = prompt + f"""\n
The following are the mediums from the gnatprove output, including the line of code the medium occurs at, and an explanation of the medium:
{medium_code_reference}
"""

        return prompt


    
    
    
    
    

            
        
    
