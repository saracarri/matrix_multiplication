
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

- Windows 11 Home
- MSYS2 UCRT64
- GCC 16.2.0
- Microsoft MPI 10.1 (MS-MPI)
- Python 3.12
- Matplotlib 3.10.8
- Windows PSAPI library

The MPI compiler was installed through MSYS2 UCRT64 using:

```bash
pacman -S mingw-w64-ucrt-x86_64-msmpi
```

Microsoft MPI Runtime was installed separately to provide `mpiexec.exe`.

The C implementation is compiled and executed from MSYS2 UCRT64. Python benchmark and plotting scripts are executed from Windows PowerShell.

The Python scripts use the following fixed path for MPI:

```text
C:\Program Files\Microsoft MPI\Bin\mpiexec.exe
```

This path must be updated if Microsoft MPI is installed elsewhere.

## Compilation

Open MSYS2 UCRT64 and navigate to the `assignment4` directory.

Compile the distributed implementation:

```bash
mpicc -O2 -std=c11 c/distributed.c -o c/distributed.exe -lpsapi
```

## Execution

Run the program by specifying the number of MPI processes and the matrix size.

For example:

```bash
mpiexec -n 4 ./c/distributed.exe 500
```

To run the program without modifying the existing result CSV files:

```bash
mpiexec -n 4 ./c/distributed.exe 500 --no-save
```

The program prints the matrix size, number of processes, validation status, memory measurements, and median and IQR of the execution times.

## Input Data

The matrices are reused from Assignments 1 and 2.

For matrix sizes up to 300, the implementation reads:

```text
../assignment1/data/A_n.csv
../assignment1/data/B_n.csv
../assignment1/data/expected/C_n.csv
```

For larger sizes, the corresponding files are read from `../assignment2/data/`.

The repository must contain `assignment1`, `assignment2` and `assignment4` as sibling directories. The program must be executed from `assignment4` so that the relative paths resolve correctly.

All matrices are square and contain integer values. The computed results are compared with the expected matrices.

The largest tested size was n=1000, which was also the maximum supported by the available input datasets and implementation. No larger configurations were attempted.

## Experimental Setup

All experiments were performed on a single computer with the following hardware:

- CPU: Intel Core Ultra 7 155H
- Physical cores: 16
- Logical processors: 22
- RAM: approximately 32 GiB
- Operating system: Windows 11 Home

No explicit process affinity was configured. All MPI processes shared the same physical machine and memory resources.

The following matrix sizes were tested:

- 100, 300, 500, 750 and 1000

The following MPI process counts were tested:

- 1, 2, 4 and 8

Each configuration used one warm-up run followed by five measured repetitions.

The median was used to summarize execution times, and the interquartile range (IQR) was used to describe variability.

All configurations were validated against the expected results.

### Execution Time

`MPI_Wtime()` measures the distributed multiplication, including broadcast, scatter, computation, gather and synchronization.

Input loading, initial memory allocation and result validation are excluded from the timed region. The initialization of the local result buffer is also performed before timing begins.

The maximum elapsed time across MPI processes is recorded for each phase.

Individual phase durations may include waiting time and should not be added together to reconstruct the total execution time.

### Memory Usage

Memory is measured using the Windows `GetProcessMemoryInfo()` function.

Two metrics are reported:

- Sum of individual process peak working sets.
- Maximum peak working set of an individual process.

Memory measurements are expressed in MiB.

The sum of individual peaks does not necessarily represent the maximum simultaneous memory consumption.

The root process stores the complete input and output matrices and loads the expected result during validation. Its memory requirements therefore differ from those of the other processes.

### End-to-End Time

A separate Python script measures the elapsed time from launching `mpiexec` until the complete program finishes.

Each end-to-end execution includes MPI initialization, input loading, memory allocation, one internal warm-up run, five measured multiplications, validation and program termination.

Five complete executions are measured per configuration, preceded by an additional unrecorded warm-up execution.

These measurements are reported separately because they represent complete benchmark sessions rather than individual matrix multiplications.

## Reproducing the Experiments

All commands below should be executed from the `assignment4` directory.

### MPI Benchmarks

Run from PowerShell:

```powershell
python scripts/run_benchmarks.py
```

This generates:

- `results/distributed_times.csv`
- `results/distributed_memory.csv`

The script tests all matrix sizes and MPI process configurations.

It does not overwrite existing results. Move or rename the current CSV files before running a new benchmark.

### End-to-End Benchmarks

Run:

```powershell
python scripts/measure_end_to_end.py
```

This generates:

- `results/distributed_end_to_end.csv`

The script uses the `--no-save` option to preserve the original timing and memory measurements.

### Generate Figures

Run:

```powershell
python scripts/plot_results.py
```

This generates the MPI performance and memory figures in the `figures/` directory.

### Comparison with Assignment 3

Run:

```powershell
python scripts/compare_methods.py
```

This generates:

- `results/methods_comparison.csv` 
- `figures/methods_comparison.png` 

The comparison uses the sequential and OpenMP results from Assignment 3.

The timing boundaries are not identical: MPI includes data distribution, result collection and synchronization, while the previous implementations measure their multiplication functions. The comparison should therefore be interpreted with this limitation in mind.

## Results

The raw measurements are stored in the `results/` directory.

The following figures were generated:

| Figure | Description |
|---|---|
| `execution_time.png` | MPI execution time across matrix sizes and process counts |
| `speedup.png` | Speedup relative to MPI with one process |
| `efficiency.png` | Parallel efficiency |
| `memory_usage.png` | Sum of individual process peak memory |
| `computation_time.png` | MPI computation time for n=1000 |
| `communication_overhead.png` | MPI communication phase durations for n=1000 |
| `methods_comparison.png` | Sequential, OpenMP and MPI execution time comparison |
| `end_to_end_time.png` | Complete MPI benchmark execution time |

The experiment showed that increasing the number of MPI processes generally improved performance for larger matrices.

For n=1000, the median MPI execution time decreased from 341.60 ms with one process to 91.52 ms with eight processes, corresponding to a speedup of approximately 3.73.

However, smaller matrices benefited less from additional processes, and memory usage increased as more processes were introduced.

## Additional Materials

The file `c/mpi_test.c` contains a simple MPI program used to verify that multiple processes could be launched correctly before implementing matrix multiplication.

The `results/preliminary/` directory contains measurements from the initial development and testing stages. These results are kept for reference but are not used in the final analysis.

The main experimental results are stored in the CSV files directly inside `results/`.

## Limitations

All MPI experiments were executed on a single computer. Therefore, the results reflect local multi-process communication rather than communication between physical machines.

The experiments were limited to the tested matrix sizes, process counts, integer inputs and available hardware.

No explicit process affinity was configured. Differences in CPU core performance, shared memory bandwidth and processor frequency may have influenced scalability, but these effects were not measured separately.

Communication phase measurements may include waiting time and do not represent isolated network transfer costs.

Furthermore, differences in timing boundaries must be considered when comparing MPI with the sequential and OpenMP implementations from Assignment 3.

The conclusions are limited to the implementations and experimental conditions evaluated in this study.
