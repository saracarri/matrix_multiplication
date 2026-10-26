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

- Windows 11 Home
- MSYS2 UCRT64 with GCC 16.2.0
- Python 3.12
- Matplotlib 3.10.8
- psutil 7.1.0

C programs were compiled using `-O2 -std=c11`.

## Reproducing the Experiments

All commands below are run from the `assignment2` directory.

### 1. Generate Input Data

Generate the dense and sparse matrices and the reference results:

```bash
python scripts/generate_inputs.py
python scripts/validate_results.py
python scripts/generate_sparse_inputs.py
```

The smaller dense matrices and their reference results are reused from `assignment1/data/`. Both assignment directories must be available.

### 2. Compile the C Programs

Using GCC in MSYS2 UCRT64:

```bash
gcc -O2 -std=c11 c/baseline.c -o c/baseline.exe
gcc -O2 -std=c11 c/reordered.c -o c/reordered.exe
gcc -O2 -std=c11 c/blocked.c -o c/blocked.exe
gcc -O2 -std=c11 c/sparse_csr.c -o c/sparse_csr.exe
```

### 3. Run the Benchmarks

Dense matrix multiplication:

```bash
./c/baseline.exe
./c/reordered.exe
./c/blocked.exe
```

Sparse matrix multiplication:

```bash
./c/sparse_csr.exe
```

Each program validates its results and saves benchmark measurements in `results/`.

Individual configurations can also be tested:

```bash
./c/reordered.exe 500
./c/sparse_csr.exe 500 90
```

Individual benchmark runs overwrite their timing CSV files. Run the executables without arguments to regenerate the complete timing datasets.

### 4. Measure Process Memory

The memory measurement scripts use Python and `psutil` to launch the C executables with the `--memory` option. Run them in an environment where the MSYS2 UCRT64 runtime libraries are available.

```bash
python scripts/measure_dense_memory.py
python scripts/measure_process_memory.py
```

The measurements are saved in `results/dense_process_memory.csv` and `results/sparse_process_memory.csv`. The memory mode does not overwrite timing or estimated-storage CSV files.

RSS is sampled approximately every millisecond, with one process execution per configuration. Sampling may not capture the exact memory peak.

### 5. Generate the Figures

```bash
python scripts/plot_dense_results.py
python scripts/plot_sparse_results.py
```

The figures are saved in `results/figures/`.

## Measurement Notes

Each timing configuration uses five measured repetitions after a warm-up. Batching is used for the smallest matrices to reduce timer noise.

CSR conversion includes both input matrices, A and B, and is measured separately from multiplication.

Estimated array storage covers the matrix representations, whereas RSS measures observed process memory, including program overhead.

The experiments were performed on a single Windows computer using sequential C implementations. Operating system activity, CPU scheduling and caching may affect execution times.