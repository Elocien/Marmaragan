import os
import shutil
from time import sleep
from src.util import generate_spark_files, retrieve_filenames_from_dir


def gen_benchmark(benchmark_dir: str):

    benchmark_files = retrieve_filenames_from_dir(benchmark_dir)
    
    benchmark_dir_name = "tmp_benchmark_dir"

    # Remove dir if it exists
    try:
        shutil.rmtree(benchmark_dir_name)
        sleep(1)
    except Exception:
        pass

    # generate temporary directory for the spark files
    os.mkdir(benchmark_dir_name)


# Iterate over each file in the benchmark and generate the files in the spark_benchmark directory
    for benchmark_file_path in benchmark_files:
        generate_spark_files(benchmark_file_path, benchmark_dir_name)
