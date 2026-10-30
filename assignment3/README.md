# Assignment 3 — Parallel Matrix Multiplication with OpenMP

## Overview

This assignment investigates how the number of threads affects the performance of dense matrix multiplication in C.

Two implementations are compared:

- **Sequential:** loop-reordered matrix multiplication (i-k-j), reused from Assignment 2.
- **Parallel:** the same algorithm using OpenMP to distribute the outermost loop across multiple threads.

The experiment evaluates execution time, memory usage, speedup and parallel efficiency.

## Requirements

The experiments were conducted on Windows 11 Home with an Intel Core Ultra 7 155H processor (16 physical cores, 22 logical processors) and 32 GiB RAM.

Software used:

- GCC 16.2.0 (MSYS2 UCRT64)
- OpenMP (GCC `-fopenmp`)
- Python 3.12
- Matplotlib 3.10.8
- psutil 7.1.0

## Project Structure

```text
assignment3/
├── c/
│   ├── sequential.c
│   └── parallel.c
├── scripts/
│   ├── run_benchmarks.sh
│   ├── measure_process_memory.py
│   ├── analyze_results.py
│   └── plot_results.py
├── results/
├── figures/
├── report/
└── README.md
```

## Input Data

The experiment reuses the input matrices from Assignments 1 and 2.

- Sizes: 100, 300, 500, 750 and 1000.
- Data type: 32-bit integers.
- Values: integers from 0 to 9.
- Random seeds: 42 for matrix A and 43 for matrix B.

Matrices up to size 300 are loaded from `assignment1/data/`. Larger matrices are loaded from `assignment2/data/`.

The corresponding reference results are used to verify correctness.

The repository must retain the original directory structure for the relative paths to work.

## Compilation

Open MSYS2 UCRT64 and navigate to the `assignment3` directory.

Compile the sequential implementation:

```bash
gcc -O2 -std=c11 c/sequential.c -o c/sequential.exe
```

Compile the parallel implementation:

```bash
gcc -O2 -std=c11 -fopenmp c/parallel.c -o c/parallel.exe
```

## Correctness Tests

Run the correctness tests before benchmarking:

```bash
./c/sequential.exe --test
OMP_NUM_THREADS=4 ./c/parallel.exe --test
```

Both implementations are tested using matrices with known results, identity matrices and zero matrices.

Experimental results are also compared with reference matrices.

## Benchmarking

The experiment uses five matrix sizes and six thread configurations: 1, 2, 4, 8, 16 and 22 threads.

Each configuration includes one warm-up execution followed by five measured repetitions.

Execution time is measured using `CLOCK_MONOTONIC`. Input loading and allocation are excluded from the timed region, while output initialisation is included.

To execute the complete benchmark:

```bash
bash scripts/run_benchmarks.sh
```

The script compiles the implementations, runs correctness tests and executes the sequential and parallel benchmarks.

It clears previously generated benchmark CSV files before starting a complete run.

Individual configurations can also be executed:

```bash
./c/sequential.exe 500
OMP_NUM_THREADS=4 ./c/parallel.exe 500
```

Raw measurements are saved in `results/`.

## Memory Measurements

Estimated array storage is calculated for the three dense matrices.

Peak process Resident Set Size (RSS) is measured separately using Python and psutil.

Run:

```bash
python scripts/measure_process_memory.py
```

The results are stored in `results/process_memory.csv`.

Memory is sampled approximately every 1 ms, so short-lived peaks may not be captured.

## Data Analysis

Generate the performance summary:

```bash
python scripts/analyze_results.py
```

This calculates median execution time, interquartile range (IQR), speedup and efficiency.

Speedup is defined as:

\[
S(p) = \frac{T_{\text{seq}}(n)}{T_p(n)}
\]

Parallel efficiency is:

\[
E(p) = \frac{S(p)}{p}
\]

Both metrics use median execution times.

The summary is saved in `results/performance_summary.csv`.

## Figures

Generate the figures using:

```bash
python scripts/plot_results.py
```

Four figures are produced in `figures/`:

- `execution_time.png`: sequential and parallel execution times.
- `speedup.png`: speedup across thread configurations.
- `efficiency.png`: parallel efficiency.
- `memory_usage.png`: peak process RSS.

## Results

Parallel execution significantly improved performance for larger matrices.

For matrices of size 1000, the maximum observed speedup was approximately **7.24× with 22 threads**.

However, using more threads did not always produce better results. For size 500, the best performance was achieved with 16 threads.

Parallel efficiency generally decreased as thread count increased, while memory consumption remained relatively similar across implementations.

These findings are limited to the tested hardware, input matrices and execution environment.

## Report

The research report is available in the `report/` directory.

It includes the experimental methodology, results, figures, discussion and conclusions.

## Use of Artificial Intelligence

ChatGPT (OpenAI) was used to assist with code development, debugging, data analysis and report writing.

All experimental measurements were obtained from local executions and reviewed by the author.