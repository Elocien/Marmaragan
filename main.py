from src.run_benchmark import *


# PARAMS


# System Message
# -----------------------------------------------------------------------
system_message="""\
You are a Spark2014/ADA programmer with strong logical reasoning abilities. 
You are tasked with fixing implemenations of Spark2014/ADA programs. You will be given an Implementation of a program, as
well as a specification of the program. You must complete the package body of the given program, inserting a single "pragma Loop_Invariant" statement.
You must not modify the code in any other way.
"""


# Prompt
# -----------------------------------------------------------------------

# Zero-shot-CoT prompt
prompt = """\n
Try to solve the following problem logically and step by step. The final answer should then be delimited in the following way:

```ada

code here

```

The following are the specifications and dependencies of a Spark2014/ADA project:

{dependencies} \n

This is the package body (implementation):

{package_body} \n

Add a single 'pragma Loop_Invariant' statement to the package body, so that the code runs error and medium free. 
Do not modify the code in any other way. Return the entire implementation file with the single addition.
"""


# # Normal Prompt
# prompt = f"""\
# The following code is a Spark2014/ADA project.\n\n
# {dependencies}


# Here are the current mediums being thrown by gnatprove, in the form of the line referenced as the cause and an explaination:\n\n
# {package_body}

# Return the fixed code for the first implementation file, delimiting with 
# ```ada

# code here

# ```
# """

                    

# Benchmark
# -----------------------------------------------------------------------
benchmark_file_path = "benchmarks/benchmark_rem_last_LoopInv"
# benchmark_file_path = "benchmarks/benchmark_rem_first_LoopInv"


# GPT Model
# -----------------------------------------------------------------------
model = "gpt-3.5-turbo-1106"
# model = "gpt-4-0125-preview"
# model = "gpt-4-0613"


# N solutions
# -----------------------------------------------------------------------
n = 1


# Retries
# -----------------------------------------------------------------------
retries = 0


# With mediums in prompt (pre-compile program with gnatprove)
# -----------------------------------------------------------------------
with_medium_in_prompt = False


# Which benchmark programs to run (default is all if option is excluded)
# -----------------------------------------------------------------------
# All programs 
# benchmark_programs = list(range(1, 17))

# # Only argu
# benchmark_programs = [2,3,4,5,6]

# # Only non-argu
# benchmark_programs = [1,7,8,9,10,11,12,13,14,15,16]

# Only copy
benchmark_programs = [7]        



# Run the benchmark
basic_benchmark = run_benchmark(
                        system_message=system_message,
                        prompt=prompt,
                        benchmark_dir=benchmark_file_path,
                        gpt_model=model,
                        n_solutions=n,
                        retries=retries,
                        with_medium_in_prompt=False,
                        benchmark_program_indices=benchmark_programs)



basic_benchmark.run()





