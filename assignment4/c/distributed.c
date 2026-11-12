#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>
#include <windows.h>
#include <psapi.h>

#define WARMUP_RUNS 1
#define REPETITIONS 5

void load_matrix(const char *filename, int n, int *matrix) {
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        fprintf(stderr, "Error opening file: %s\n", filename);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    for (int i = 0; i < n * n; i++) {
        if (fscanf(file, "%d", &matrix[i]) != 1) {
            fprintf(stderr, "Error reading file: %s\n", filename);
            fclose(file);
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        if (i < n * n - 1) {
            int separator = fgetc(file);

            if (separator != ',' && separator != EOF) {
                ungetc(separator, file);
            }
        }
    }

    fclose(file);
}

void get_filename(char *filename, size_t length,
                  int n, const char *matrix) {
    const char *directory = (n <= 300)
        ? "../assignment1/data"
        : "../assignment2/data";

    if (strcmp(matrix, "C") == 0) {
        snprintf(filename, length,
                 "%s/expected/C_%d.csv", directory, n);
    } else {
        snprintf(filename, length,
                 "%s/%s_%d.csv", directory, matrix, n);
    }
}

int validate_matrix(int n, const int *C) {
    int *expected = malloc((size_t)n * n * sizeof(int));

    if (expected == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    char filename[256];
    get_filename(filename, sizeof(filename), n, "C");
    load_matrix(filename, n, expected);

    int correct = 1;

    for (int i = 0; i < n * n; i++) {
        if (C[i] != expected[i]) {
            correct = 0;
            break;
        }
    }

    free(expected);
    return correct;
}

void multiply_local(int n, int rows,
                    const int *A, const int *B, int *C) {
    for (int i = 0; i < rows; i++) {
        for (int k = 0; k < n; k++) {
            for (int j = 0; j < n; j++) {
                C[i * n + j] += A[i * n + k] * B[k * n + j];
            }
        }
    }
}

int compare_doubles(const void *a, const void *b) {
    double x = *(const double *)a;
    double y = *(const double *)b;
    return (x > y) - (x < y);
}

void summarize(const double values[REPETITIONS],
               double *median, double *iqr) {
    double sorted[REPETITIONS];

    memcpy(sorted, values, sizeof(sorted));
    qsort(sorted, REPETITIONS, sizeof(double), compare_doubles);

    // Tukey hinges for five observations
    *median = sorted[2];
    *iqr = sorted[3] - sorted[1];
}

double get_peak_memory_mib(void) {
    PROCESS_MEMORY_COUNTERS counters;

    if (GetProcessMemoryInfo(
            GetCurrentProcess(),
            &counters,
            sizeof(counters))) {

        return (double)counters.PeakWorkingSetSize /
               (1024.0 * 1024.0);
    }

    return -1.0;
}

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2 && argc != 3) {
        if (rank == 0)
            fprintf(stderr, "Usage: distributed.exe <size> [--no-save]\n");
        MPI_Finalize();
        return 1;
    }

    int save_results = 1;

    if (argc == 3) {
        if (strcmp(argv[2], "--no-save") != 0) {
            if (rank == 0)
                fprintf(stderr, "Unknown option: %s\n", argv[2]);
            MPI_Finalize();
            return 1;
        }

        save_results = 0;
    }

    char *end;
    long parsed_n = strtol(argv[1], &end, 10);

    if (*end != '\0' || parsed_n <= 0 || parsed_n > 1000) {
        if (rank == 0)
            fprintf(stderr, "Invalid matrix size\n");
        MPI_Finalize();
        return 1;
    }

    int n = (int)parsed_n;
    size_t elements = (size_t)n * n;

    int *A = NULL;
    int *C = NULL;
    int *B = malloc(elements * sizeof(int));

    int *sendcounts = malloc(size * sizeof(int));
    int *displs = malloc(size * sizeof(int));

    if (!B || !sendcounts || !displs) {
        fprintf(stderr, "Memory allocation failed\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    int offset = 0;

    for (int p = 0; p < size; p++) {
        int rows = n / size + (p < n % size ? 1 : 0);
        sendcounts[p] = rows * n;
        displs[p] = offset;
        offset += sendcounts[p];
    }

    int local_rows = sendcounts[rank] / n;
    size_t local_elements = (size_t)local_rows * n;
    size_t local_capacity = local_elements ? local_elements : 1;

    int *local_A = malloc(local_capacity * sizeof(int));
    int *local_C = calloc(local_capacity, sizeof(int));

    if (!local_A || !local_C) {
        fprintf(stderr, "Local memory allocation failed\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    if (rank == 0) {
        A = malloc(elements * sizeof(int));
        C = malloc(elements * sizeof(int));

        if (!A || !C) {
            fprintf(stderr, "Memory allocation failed\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        char filename[256];

        get_filename(filename, sizeof(filename), n, "A");
        load_matrix(filename, n, A);

        get_filename(filename, sizeof(filename), n, "B");
        load_matrix(filename, n, B);
    }

    FILE *csv = NULL;

    if (rank == 0 && save_results) {
        csv = fopen("results/distributed_times.csv", "a+");

        if (!csv) {
            fprintf(stderr, "Cannot open results CSV\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        fseek(csv, 0, SEEK_END);

        if (ftell(csv) == 0) {
            fprintf(csv,
                "n,processes,repetition,total_ms,"
                "broadcast_ms,scatter_ms,compute_ms,gather_ms\n");
        }
    }

    double total_samples[REPETITIONS];
    double broadcast_samples[REPETITIONS];
    double scatter_samples[REPETITIONS];
    double compute_samples[REPETITIONS];
    double gather_samples[REPETITIONS];

    for (int run = 0;
         run < WARMUP_RUNS + REPETITIONS;
         run++) {

        memset(local_C, 0, local_capacity * sizeof(int));

        MPI_Barrier(MPI_COMM_WORLD);
        double total_start = MPI_Wtime();

        double start = MPI_Wtime();

        MPI_Bcast(B, n * n, MPI_INT, 0, MPI_COMM_WORLD);

        double broadcast_time = MPI_Wtime() - start;

        start = MPI_Wtime();

        MPI_Scatterv(A, sendcounts, displs, MPI_INT,
                     local_A, sendcounts[rank], MPI_INT,
                     0, MPI_COMM_WORLD);

        double scatter_time = MPI_Wtime() - start;

        start = MPI_Wtime();

        multiply_local(n, local_rows, local_A, B, local_C);

        double compute_time = MPI_Wtime() - start;

        start = MPI_Wtime();

        MPI_Gatherv(local_C, sendcounts[rank], MPI_INT,
                    C, sendcounts, displs, MPI_INT,
                    0, MPI_COMM_WORLD);

        double gather_time = MPI_Wtime() - start;

        MPI_Barrier(MPI_COMM_WORLD);

        double total_time = MPI_Wtime() - total_start;

        double local_times[5] = {
            total_time,
            broadcast_time,
            scatter_time,
            compute_time,
            gather_time
        };

        double max_times[5] = {0};

        MPI_Reduce(local_times, max_times, 5,
                   MPI_DOUBLE, MPI_MAX, 0,
                   MPI_COMM_WORLD);

        if (rank == 0) {
            if (!validate_matrix(n, C)) {
                fprintf(stderr,
                        "Validation: FAIL (run %d)\n", run);
                MPI_Abort(MPI_COMM_WORLD, 1);
            }

            if (run >= WARMUP_RUNS) {
                int r = run - WARMUP_RUNS;

                total_samples[r] = max_times[0] * 1000;
                broadcast_samples[r] = max_times[1] * 1000;
                scatter_samples[r] = max_times[2] * 1000;
                compute_samples[r] = max_times[3] * 1000;
                gather_samples[r] = max_times[4] * 1000;

                if (save_results) {
                    fprintf(csv,
                        "%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f\n",
                        n, size, r + 1,
                        total_samples[r],
                        broadcast_samples[r],
                        scatter_samples[r],
                        compute_samples[r],
                        gather_samples[r]);
                }
            }
        }
    }

    double local_memory = get_peak_memory_mib();

    double total_peak_memory = 0.0;
    double max_worker_memory = 0.0;

    MPI_Reduce(&local_memory, &total_peak_memory, 1,
            MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    MPI_Reduce(&local_memory, &max_worker_memory, 1,
            MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
            
    if (rank == 0) {
        double median, iqr;

        printf("\nMatrix size: %d x %d\n", n, n);
        printf("MPI processes: %d\n", size);
        printf("Warm-up runs: %d\n", WARMUP_RUNS);
        printf("Measured repetitions: %d\n", REPETITIONS);
        printf("Validation: PASS\n");
        printf("Sum of worker peak memory: %.2f MiB\n",
       total_peak_memory);
        printf("Maximum worker peak memory: %.2f MiB\n",
       max_worker_memory);
       
               if (save_results) {
            FILE *memory_csv = fopen("results/distributed_memory.csv", "a+");

            if (memory_csv == NULL) {
                fprintf(stderr, "Cannot open memory results CSV\n");
                MPI_Abort(MPI_COMM_WORLD, 1);
            }

            fseek(memory_csv, 0, SEEK_END);

            if (ftell(memory_csv) == 0) {
                fprintf(memory_csv,
                        "n,processes,sum_worker_peak_mib,max_worker_peak_mib\n");
            }

            fprintf(memory_csv, "%d,%d,%.6f,%.6f\n",
                    n, size, total_peak_memory, max_worker_memory);

            fclose(memory_csv);
        }

        const char *labels[5] = {
            "Total", "Broadcast", "Scatter",
            "Computation", "Gather"
        };

        const double *samples[5] = {
            total_samples, broadcast_samples,
            scatter_samples, compute_samples,
            gather_samples
        };

        printf("\nMedian and IQR (ms):\n");

        for (int i = 0; i < 5; i++) {
            summarize(samples[i], &median, &iqr);
            printf("%-13s %.6f (IQR: %.6f)\n",
                   labels[i], median, iqr);
        }

        if (csv != NULL) {
            fclose(csv);
        }
    }

    free(A);
    free(B);
    free(C);
    free(local_A);
    free(local_C);
    free(sendcounts);
    free(displs);

    MPI_Finalize();
    return 0;
}
