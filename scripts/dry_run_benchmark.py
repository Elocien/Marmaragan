import shutil
from time import sleep
from src.util import *


def dry_run_benchmark(benchmark_dir: str) -> None:
    """
    This script generates the spark files for a given benchmark, runs gnatprove on each of the programs in the benchmark
    and returns which files are medium free and which aren't.
    
    Args:
        benchmark_dir: The directory containing the benchmark files
        
    Returns:
        None
    """
    benchmark_files = retrieve_filenames_from_dir(benchmark_dir)
    tmp_benchmark = "tmp_" + benchmark_dir.split("/")[-1]

    # Remove dir if it exists
    try:
        shutil.rmtree(tmp_benchmark)
        sleep(1)
    except Exception:
        pass

    # generate temporary directory for the spark files
    os.mkdir(tmp_benchmark)


    # Iterate over each file in the benchmark and generate the files in the spark_benchmark directory
    for benchmark_file_path in benchmark_files:
        generated_gpr_file = generate_spark_files(benchmark_file_path, tmp_benchmark)

        # Run gnatprove
        output = run_gnatprove(generated_gpr_file)
        
        # Write the output to a file
        with open(benchmark_dir.split("/")[-1] + "_results.txt", "a") as f:
            f.write("\n\n\n\n" + benchmark_file_path)
            f.write("\nCompilation successful: " + str(is_compilation_successful(output)))
            f.write("\n\nMediums: \n" + str(parse_gnatprove_output(output)))
            f.write("\n\nOutput:\n" + str(output))
            f.write("--------------------------------------------------\n")
        
    
    # Remove the tmp_benchmark directory
    # shutil.rmtree(tmp_benchmark)
