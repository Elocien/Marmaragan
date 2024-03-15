from scripts.gen_benchmark_diff import calculate_diff_with_line_numbers
from scripts.gen_benchmark import gen_benchmark



# Generate the spark benchmark files
# gen_benchmark(benchmark_dir="benchmarks/benchmark_rem_last_LoopInv")
gen_benchmark(benchmark_dir="benchmarks/benchmark/code")

# Generate the diff between the original and modified benchmark
# original_dir = 'benchmarks/benchmark/code'
# modified_dir = 'benchmarks/benchmark_rem_last_LoopInv'
# differences = calculate_diff_with_line_numbers(original_dir, modified_dir)

# for diff in differences:
#     print(f"{diff[0]}:{diff[1]}, Deletion: {diff[2]}")
