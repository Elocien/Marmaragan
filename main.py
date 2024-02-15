from src.gen_n import *


# GPT Model to use

model = "gpt-3.5-turbo-1106"
# model = "gpt-4-0125-preview"
# model = "gpt-4-0613"




# Run the benchmark
basic_benchmark = gen_1(instructions=
                        """\
                        You are a Spark2014/ADA programmer. You must complete the package body of the given program, inserting a single "pragma Loop_Invariant"
                        statement directly within a "loop" statement. E.g. a statement such as "pragma Loop_Variant (Increases => L.Size);"
                        Return only the code of the amended package body, with the single addition. Do not modify any other parts of the code!\
                        """, 
                        benchmark_dir="benchmarks/benchmark_rem_first_LoopInv",
                        gpt_model=model)



basic_benchmark.run_benchmark()





