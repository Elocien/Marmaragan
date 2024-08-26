from scripts.gen_benchmark_diff import calculate_diff_with_line_numbers
from scripts.gen_benchmark import gen_benchmark
from scripts.dry_run_benchmark import dry_run_benchmark



# GEN BENCHMARK FILES
# gen_benchmark(benchmark_dir="benchmarks/2-all_pragmas")
# gen_benchmark(benchmark_dir="benchmarks/1-benchmark/code")






# GEN DIFF

# Generate the diff between the original and modified benchmark
original_dir = 'benchmarks/baseline-programs'
modified_dir = 'benchmarks/3-one_assert'
differences = calculate_diff_with_line_numbers(original_dir, modified_dir)

for diff in differences:
    print(f"{diff[0]}:{diff[1]}, Deletion: {diff[2]}")




# DRY RUN
# dry_run_benchmark(benchmark_dir="benchmarks/2-all_pragmas")
# dry_run_benchmark(benchmark_dir="benchmarks/3-last_invariant_per_loop")
# dry_run_benchmark(benchmark_dir="benchmarks/4-one_assert")
# dry_run_benchmark(benchmark_dir="benchmarks/5-all_invariants_one_loop")
# dry_run_benchmark(benchmark_dir="benchmarks/6-last_invariant_one_loop")
