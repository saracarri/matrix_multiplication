
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

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

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2) {
        if (rank == 0) {
            fprintf(stderr, "Usage: distributed.exe <size>\n");
        }
        MPI_Finalize();
        return 1;
    }

    char *end;
    long parsed_n = strtol(argv[1], &end, 10);

    if (*end != '\0' || parsed_n <= 0 || parsed_n > 1000) {
        if (rank == 0) {
            fprintf(stderr, "Invalid matrix size\n");
        }
        MPI_Finalize();
        return 1;
    }

    int n = (int)parsed_n;
    size_t elements = (size_t)n * n;

    double start, total_start;
    double broadcast_time, scatter_time;
    double compute_time, gather_time;
    double total_time;

    double max_broadcast, max_scatter;
    double max_compute, max_gather;
    double max_total;

    int *A = NULL;
    int *C = NULL;
    int *B = malloc(elements * sizeof(int));

    int *sendcounts = malloc(size * sizeof(int));
    int *displs = malloc(size * sizeof(int));

    if (B == NULL || sendcounts == NULL || displs == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Calculate row distribution
    int offset = 0;

    for (int p = 0; p < size; p++) {
        int rows = n / size + (p < n % size ? 1 : 0);

        sendcounts[p] = rows * n;
        displs[p] = offset;
        offset += sendcounts[p];
    }

    int local_rows = sendcounts[rank] / n;
    size_t local_elements = (size_t)local_rows * n;

    // Allocate at least one element for empty partitions
    int *local_A = malloc((local_elements ?
                           local_elements : 1) * sizeof(int));

    int *local_C = calloc(local_elements ?
                          local_elements : 1, sizeof(int));

    if (local_A == NULL || local_C == NULL) {
        fprintf(stderr, "Local memory allocation failed\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    if (rank == 0) {
        A = malloc(elements * sizeof(int));
        C = malloc(elements * sizeof(int));

        if (A == NULL || C == NULL) {
            fprintf(stderr, "Memory allocation failed\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        char filename[256];

        get_filename(filename, sizeof(filename), n, "A");
        load_matrix(filename, n, A);

        get_filename(filename, sizeof(filename), n, "B");
        load_matrix(filename, n, B);
    }


    // Synchronize processes before measurement
    MPI_Barrier(MPI_COMM_WORLD);
    total_start = MPI_Wtime();

    // Broadcast matrix B
    start = MPI_Wtime();

    MPI_Bcast(B, n * n, MPI_INT, 0, MPI_COMM_WORLD);

    broadcast_time = MPI_Wtime() - start;

    // Distribute rows of A
    start = MPI_Wtime();

    MPI_Scatterv(A, sendcounts, displs, MPI_INT,
                 local_A, sendcounts[rank], MPI_INT,
                 0, MPI_COMM_WORLD);

    scatter_time = MPI_Wtime() - start;

    // Compute local matrix multiplication
    start = MPI_Wtime();

    multiply_local(n, local_rows, local_A, B, local_C);

    compute_time = MPI_Wtime() - start;

    // Collect partial results
    start = MPI_Wtime();

    MPI_Gatherv(local_C, sendcounts[rank], MPI_INT,
                C, sendcounts, displs, MPI_INT,
                0, MPI_COMM_WORLD);

    gather_time = MPI_Wtime() - start;

    // Synchronize before ending measurement
    MPI_Barrier(MPI_COMM_WORLD);
    total_time = MPI_Wtime() - total_start;

    // Report maximum elapsed time across processes
    MPI_Reduce(&broadcast_time, &max_broadcast, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    MPI_Reduce(&scatter_time, &max_scatter, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    MPI_Reduce(&compute_time, &max_compute, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    MPI_Reduce(&gather_time, &max_gather, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    MPI_Reduce(&total_time, &max_total, 1,
               MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);


    if (rank == 0) {
        printf("Matrix size: %d x %d\n", n, n);
        printf("MPI processes: %d\n", size);
        printf("Total time: %.6f ms\n", max_total * 1000);
        printf("Broadcast time: %.6f ms\n", max_broadcast * 1000);
        printf("Scatter time: %.6f ms\n", max_scatter * 1000);
        printf("Computation time: %.6f ms\n", max_compute * 1000);
        printf("Gather time: %.6f ms\n", max_gather * 1000);

        if (validate_matrix(n, C)) {
            printf("Validation: PASS\n");
        } else {
            printf("Validation: FAIL\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
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
