from src.gen_n import *
from scripts.gen_benchmark import gen_benchmark



# Run the benchmark
basic_benchmark = gen_1(instructions=
                        """\
                        You are a Spark2014/ADA programmer. Given code in the form of an implementation (adb), specification (ads)
                        and additional dependencies , fix the code so that it runs error free. The compile errors (mediums) from gnatprove
                        are additionally given. Fix the code so that no mediums occur.
                        Return only the fixed code for the first implemenation file.\
                        """, 
                        benchmark_dir="spark_projects/benchmark/code")

basic_benchmark.run_benchmark()



# Generate the spark benchmark files
# gen_benchmark(benchmark_dir="spark_projects/benchmark/code")


