from src.gen_n import *
from scripts.gen_benchmark import gen_benchmark



# Run the benchmark
basic_benchmark = gen_1(instructions=
                        """\
                        You are a Spark2014/ADA programmer. Given code in the form of an implementation (adb), specification (ads)
                        and additional dependencies , fix the code so that it runs error free. The compile errors (mediums) from gnatprove
                        are additionally given. Fix the code by adding a single pragma Loop_Invariant statement. 
                        Return a single file, with the code appropriatly fixed.\
                        """, 
                        benchmark_dir="spark_projects/benchmark_rem_first_LoopInv",
                        gpt_model="gpt-4-0613")

# gpt_model (str): The GPT model to use. Choice of "gpt-3.5-turbo-1106", "gpt-4-0125-preview" or "gpt-4-0613"

basic_benchmark.run_benchmark()



# Generate the spark benchmark files
# gen_benchmark(benchmark_dir="spark_projects/benchmark_rem_first_LoopInv")


