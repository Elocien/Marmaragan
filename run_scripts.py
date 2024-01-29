from scripts.gen_benchmark_diff import calculate_diff_with_line_numbers
from scripts.gen_benchmark import gen_benchmark



# Generate the spark benchmark files
# gen_benchmark(benchmark_dir="spark_projects/benchmark_rem_first_LoopInv")

# # Generate the diff between the original and modified benchmark
original_dir = 'spark_projects/benchmark/code'
modified_dir = 'spark_projects/benchmark_rem_first_LoopInv'
differences = calculate_diff_with_line_numbers(original_dir, modified_dir)

for diff in differences:
    print(f"{diff[0]}:{diff[1]}, Deletion: {diff[2]}")
