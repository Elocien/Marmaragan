from src.gen_n import *
from scripts.gen_benchmark import gen_benchmark



# Run the benchmark
basic_benchmark = gen_1(instructions=
                        """\
                        You are a Spark2014/ADA programmer. Given code in the form of an implementation (adb), specification (ads)
                        and additional dependencies , fix the code so that it runs error free. The compile errors (mediums) from gnatprove
                        are additionally given. Fix the code by adding a single pragma Loop_Invariant statement. 
                        Return only the fixed code for a single file.\
                        """, 
                        benchmark_dir="spark_projects/benchmark_rem_first_LoopInv",
                        gpt_model = "gpt-3.5-turbo-1106")

basic_benchmark.run_benchmark()



# Generate the spark benchmark files
# gen_benchmark(benchmark_dir="spark_projects/benchmark_rem_first_LoopInv")


