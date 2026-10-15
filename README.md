
# Matrix Multiplication Benchmark

Big Data - Individual Assignment 1  
Universidad de Las Palmas de Gran Canaria  
Academic year 2026-2027

## Objective

This project compares the execution time and memory usage of basic matrix multiplication implemented in Python, Java and C.

All three implementations use the standard triple-loop algorithm, with O(n³) time complexity.

## Project Structure

- `python/`: Python implementation and benchmarking.
- `java/`: Java implementation and benchmarking.
- `c/`: C implementation and benchmarking.
- `scripts/`: Input generation, validation, memory measurements and plotting scripts.
- `data/`: Shared input matrices and expected results.
- `results/`: Raw CSV measurements and generated figures.
- `report/`: Research report.

## Experimental Setup

The experiments were performed on the following system:

- CPU: Intel Core Ultra 7 155H
- Physical cores: 16
- Logical processors: 22
- RAM: approximately 32 GB
- OS: Windows 11 Home
- Python: 3.12.6
- Java: OpenJDK Temurin 17.0.15
- C compiler: GCC 16.2.0 (MSYS2 UCRT64)

Matrix sizes: 10, 50, 100, 200 and 300.

The matrices contain integers between 0 and 9 and were generated using Python's random number generator with seeds 42 and 43.

All implementations use the same input CSV files and the same i-j-k loop order.

Each configuration uses five measured repetitions. Python and C use one warm-up execution, while Java uses ten.

The output matrix is allocated before timing. Each timed multiplication resets the output elements to zero.

For C with n = 10, each measurement uses a batch of 1000 multiplications and reports the average time per multiplication.

## Requirements

- Python 3.12.6
- Java JDK 17
- GCC with C11 support
- Python packages: matplotlib and psutil

Install the Python dependencies:

```bash
python -m pip install matplotlib psutil
```

## Running the Experiments

All commands should be executed from the project root directory.

### Generate Input Matrices

```bash
python scripts/generate_inputs.py
python scripts/validate_results.py
```

### Python

```bash
python python/matrix_multiplication.py
```

### Java

Compile:

```bash
javac java/MatrixMultiplication.java
```

Run:

```bash
java -cp java MatrixMultiplication
```

### C

Compile using MSYS2 UCRT64:

```bash
gcc -std=c11 -O2 -Wall -Wextra c/matrix_multiplication.c -o c/matrix_multiplication.exe
```

Run:

```bash
./c/matrix_multiplication.exe
```

Each implementation can also be executed for a single matrix size by passing the size as an argument.

## Memory Measurements

The theoretical array storage is calculated from the dimensions and numeric types.

Process memory is measured separately using psutil, which samples the resident set size (RSS) during execution.

Run:

```bash
python scripts/measure_process_memory.py
```

The reported peak RSS is the highest observed sample, not necessarily the true instantaneous peak. It includes the language runtime and other process allocations.

## Results and Figures

Raw execution-time measurements and memory results are saved in the `results/` directory.

Generate the figures using:

```bash
python scripts/plot_results.py
```

The script creates:

- `execution_time.png`
- `execution_time_log.png`
- `memory_usage.png`

These files are saved in `results/figures/`.


The median execution times and interquartile ranges (IQR) can be calculated directly from the raw CSV measurements using:

```bash
python scripts/check_results.py
```

This script displays the median and IQR for each matrix size in Python, Java and C, allowing the reported results to be verified.

## Correctness

The implementations were checked using known small matrices, including identity and zero matrices.

Reference results were also generated for the shared input matrices. Java and C compare their complete output matrices against these reference results. Python checks its results against a reference implementation.

## Limitations

The results describe these specific implementations and execution conditions, rather than the general performance of the programming languages.

Runtime optimisation, memory management, measurement overhead and operating system activity may affect the observed results.

Memory estimates and observed RSS represent different quantities and should not be interpreted as equivalent.
