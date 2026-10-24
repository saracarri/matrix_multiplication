# Assignment 2 — Optimised Matrix Multiplication and Sparse Matrices

Big Data — Academic Year 2026/2027

## Overview

This assignment investigates the performance of different matrix multiplication approaches in C. It is divided into two parts: dense matrix optimisation and sparse matrix multiplication.

The experiments compare execution time, memory usage and scalability using matrices of different sizes. All implementations are sequential and use integer values.

## Part A — Dense Matrix Optimisation

Three methods were implemented:

- **Baseline:** Standard matrix multiplication using three nested loops in `i-j-k` order, reused from Assignment 1.
- **Loop Reordering:** Changes the loop order to `i-k-j` to improve memory access patterns.
- **Cache Blocking:** Divides the multiplication into blocks of size 32 × 32 to improve cache locality.

The methods were tested with matrices of sizes 10, 50, 100, 200, 300, 500, 750 and 1000.

The smaller input matrices and reference results were reused from Assignment 1. Larger matrices were generated with fixed random seeds (42 and 43), using integer values between 0 and 9.

## Part B — Sparse Matrix Multiplication

Sparse multiplication was implemented using the Compressed Sparse Row (CSR) representation.

The implementation stores nonzero values, their column indices and row pointers. The input matrices are converted to CSR, while the result is stored as a dense matrix.

CSR multiplication was compared with the dense `i-k-j` method using matrices of sizes 100, 300, 500, 750 and 1000.

Four sparsity levels were tested: 50%, 90%, 95% and 99% zero entries. Nonzero positions were selected randomly using fixed seeds, and their values range from 1 to 9.

Conversion time was measured separately from multiplication time.

## Experimental Methodology

All implementations were compiled using GCC with the `-O2` optimisation flag and executed in a Windows environment using MSYS2 UCRT64.

Execution times were measured using `clock_gettime(CLOCK_MONOTONIC)`. Each configuration included one warm-up run and five measured repetitions.

Results were summarised using the median and interquartile range (IQR). Small configurations used repeated multiplication batches to reduce timing noise.

Correctness was checked using known results, identity and zero matrices, and comparisons against reference implementations.

Memory was analysed using estimated array storage and peak process Resident Set Size (RSS), measured with Python and `psutil`.

## Project Structure

```text
assignment2/
├── c/
│   ├── baseline.c
│   ├── reordered.c
│   ├── blocked.c
│   └── sparse_csr.c
├── data/
│   ├── expected/
│   └── sparse/
├── scripts/
├── results/
│   └── figures/
├── report/
└── README.md
```

## Requirements

- GCC (MSYS2 UCRT64)
- Python 3.12
- matplotlib
- psutil

## Compilation

From the `assignment2` directory in MSYS2 UCRT64:

```bash
gcc -O2 -std=c11 c/baseline.c -o c/baseline.exe
gcc -O2 -std=c11 c/reordered.c -o c/reordered.exe
gcc -O2 -std=c11 c/blocked.c -o c/blocked.exe
gcc -O2 -std=c11 c/sparse_csr.c -o c/sparse_csr.exe
```

## Running the Experiments

### Part A

Run all matrix sizes:

```bash
./c/baseline.exe
./c/reordered.exe
./c/blocked.exe
```

A specific size can also be tested:

```bash
./c/reordered.exe 500
```

### Part B

Run all sparse configurations:

```bash
./c/sparse_csr.exe
```

Or select a size and sparsity level:

```bash
./c/sparse_csr.exe 500 90
```

Running an individual configuration overwrites that method's CSV results. Run the programs without arguments to regenerate the complete benchmark files.

## Data Generation and Analysis

From the `assignment2` directory:

```bash
python scripts/generate_inputs.py
python scripts/validate_results.py
python scripts/generate_sparse_inputs.py
```

The input generation scripts use fixed random seeds so that the datasets can be reproduced.

Generate the figures with:

```bash
python scripts/plot_dense_results.py
python scripts/plot_sparse_results.py
```

Process memory measurements can be reproduced using:

```bash
python scripts/measure_dense_memory.py
python scripts/measure_process_memory.py
```

The memory scripts launch the compiled C executables and should be run in an environment where the MSYS2 UCRT64 runtime libraries are available.

The raw measurements are stored in `results/`, and the generated figures are saved in `results/figures/`.

## Notes

Execution times include the multiplication operations and output initialisation, but exclude input loading and correctness validation. CSR conversion is measured separately.

The reported array-storage estimates do not represent total process memory. Peak RSS includes other allocations and runtime overhead.

The results describe the tested implementations, inputs and execution environment, rather than the performance of all possible dense or sparse multiplication algorithms.