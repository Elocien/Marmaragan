from src.gen_n import *


# GPT Model to use

# model = "gpt-3.5-turbo-1106"
# model = "gpt-4-0125-preview"
model = "gpt-4-0613"




# Run the benchmark
basic_benchmark = run_benchmark(system_message=
                        # """\
                        # You are a Spark2014/ADA programmer. You must complete the package body of the given program, inserting a single "pragma Loop_Invariant"
                        # statement directly within a "loop" statement. E.g. a statement such as "pragma Loop_Variant (Increases => L.Size);"
                        # Return only the code of the amended package body, with the single addition. Do not modify any other parts of the code!\
                        # """, 
                        """\
                        You are a Spark2014/ADA programmer with strong logical reasoning abilities. 
                        You are tasked with fixing implemenations of Spark2014/ADA programs. You will be given an Implementation of a program, as
                        well as a specification of the program. You must complete the package body of the given program, inserting a single "pragma Loop_Invariant" statement.
                        You must not modify the code in any other way.
                        """, 
                        benchmark_dir="benchmarks/benchmark_rem_first_LoopInv",
                        gpt_model=model)



basic_benchmark.chain_of_thoughts()





