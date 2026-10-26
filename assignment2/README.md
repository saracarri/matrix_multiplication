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

## Reproducing the Experiments

The experiments should be executed in the following order. All paths are relative to the \`assignment2\` directory.

### 1. Generate Input Data

Python is used to generate the dense and sparse input matrices and the reference results.

\`\`\`bash
python scripts/generate_inputs.py
python scripts/validate_results.py
python scripts/generate_sparse_inputs.py
\`\`\`

The smaller dense matrices and their reference results are reused from \`assignment1/data/\`. Both assignment directories must therefore be available.

### 2. Compile the C Programs

Using GCC in MSYS2 UCRT64:

\`\`\`bash
gcc -O2 -std=c11 c/baseline.c -o c/baseline.exe
gcc -O2 -std=c11 c/reordered.c -o c/reordered.exe
gcc -O2 -std=c11 c/blocked.c -o c/blocked.exe
gcc -O2 -std=c11 c/sparse_csr.c -o c/sparse_csr.exe
\`\`\`

### 3. Run the Benchmarks

For dense matrix multiplication:

\`\`\`bash
./c/baseline.exe
./c/reordered.exe
./c/blocked.exe
\`\`\`

For sparse matrix multiplication:

\`\`\`bash
./c/sparse_csr.exe
\`\`\`

Each program performs correctness checks and saves its benchmark measurements in \`results/\`.

An individual dense size or sparse configuration can also be executed:

\`\`\`bash
./c/reordered.exe 500
./c/sparse_csr.exe 500 90
\`\`\`

Individual benchmark runs overwrite the corresponding timing CSV files. The complete datasets can be restored by running the programs without arguments.

### 4. Measure Process Memory

The memory measurement scripts use Python and \`psutil\` to launch the C executables with the \`--memory\` option.

Run the scripts from an environment where the MSYS2 UCRT64 runtime libraries are available:

\`\`\`bash
python scripts/measure_dense_memory.py
python scripts/measure_process_memory.py
\`\`\`

These scripts save the observed process RSS in:

- \`results/dense_process_memory.csv\`
- \`results/sparse_process_memory.csv\`

The memory mode does not overwrite the timing or estimated-storage CSV files. RSS is sampled approximately every millisecond, with one process execution per configuration.

### 5. Generate the Figures

\`\`\`bash
python scripts/plot_dense_results.py
python scripts/plot_sparse_results.py
\`\`\`

The figures are saved in \`results/figures/\`.

## Measurement Notes

Each timing configuration uses five measured repetitions after a warm-up. For small matrix sizes, repeated multiplication batches are used to reduce timing noise.

CSR conversion measures the conversion of both input matrices, A and B, separately from multiplication.

The array-storage estimates represent the memory required by the selected matrix representations, while RSS measures the observed memory consumption of the complete process. RSS measurements are obtained by sampling and may not capture the exact peak.

The measurements were performed on a single Windows computer using sequential C implementations. Differences in operating system activity, CPU scheduling and cache behaviour may influence execution times.

The results apply to the tested implementations and input configurations.