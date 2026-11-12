
# Assignment 4 - Distributed Matrix Multiplication

Big Data - Individual Assignment 4  
Data Science and Engineering, ULPGC

## Objective

This assignment investigates the performance and scalability of distributed matrix multiplication using MPI in C.

The main objective is to study how the number of processes affects execution time, memory usage and communication overhead. The MPI implementation is also compared with the sequential and OpenMP implementations developed in Assignment 3.

All MPI experiments were executed on a single Windows computer, as permitted by the instructor. Therefore, the study evaluates local multi-process execution rather than communication between physical machines.

## Implementation

The distributed implementation uses the same `i-k-j` multiplication algorithm and integer matrices as the previous assignments.

The computation is divided among MPI processes:

1. Process 0 loads matrices A and B from CSV files.
2. `MPI_Bcast` distributes matrix B to all processes.
3. `MPI_Scatterv` distributes rows of A among processes.
4. Each process computes its assigned rows of C.
5. `MPI_Gatherv` collects the partial results in process 0.
6. The result is validated against the expected output.

`MPI_Scatterv` and `MPI_Gatherv` support uneven row distributions when the matrix size is not divisible by the process count.

## Requirements

- Windows
- MSYS2 UCRT64
- GCC 16.2.0
- Microsoft MPI 10.1 (MS-MPI)
- Python 3.12
- Matplotlib
- Microsoft MPI Runtime
- Windows PSAPI library

Python is used for running benchmarks and generating the results and figures.

## Compilation

Open MSYS2 UCRT64 and navigate to the `assignment4` directory.

Compile the distributed implementation:

```bash
mpicc -O2 -std=c11 c/distributed.c -o c/distributed.exe -lpsapi
```

## Execution

Run the program with a specified number of MPI processes and matrix size.

For example:

```bash
mpiexec -n 4 ./c/distributed.exe 500
```

To execute the program without modifying the result CSV files:

```bash
mpiexec -n 4 ./c/distributed.exe 500 --no-save
```

The program prints the matrix size, process count, validation status, memory measurements, and median and IQR of the execution times.

## Input Data

The matrices are reused from Assignments 1 and 2.

For sizes up to 300, the implementation reads:

```text
assignment1/data/A_n.csv
assignment1/data/B_n.csv
assignment1/data/expected/C_n.csv
```

For larger sizes, it reads the corresponding files from `assignment2/data/`.

All matrices are square and use integer values. The computed results are compared with the expected matrices.

The program must be executed from the `assignment4` directory so that the relative paths resolve correctly.

## Experimental Setup

The following matrix sizes were tested:

- 100, 300, 500, 750 and 1000

The following MPI process counts were tested:

- 1, 2, 4