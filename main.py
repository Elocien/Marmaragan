from src.gen_n import *


basic_benchmark = gen_1(instructions=
                        """\
                        You are a Spark2014/ADA programmer. Given code in the form of an implementation (abd), specification (ads)
                        and additional dependencies , fix the code so that it runs error free. The compile errors (mediums) from gnatprove
                        are additionally given. Fix the code by adding Pragma Loop_Invariant statements.
                        Return only the fixed code for the first implemenation file.\
                        """, 
                        benchmark_dir="spark_projects/benchmark/code")

basic_benchmark.run_benchmark()








