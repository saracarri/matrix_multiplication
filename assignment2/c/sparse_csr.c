
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    int n;
    int nnz;
    int *values;
    int *col_index;
    int *row_ptr;
} CSRMatrix;

CSRMatrix dense_to_csr(int n, int A[n][n]) {
    CSRMatrix csr;
    csr.n = n;
    csr.nnz = 0;

    // Count nonzero elements
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (A[i][j] != 0) {
                csr.nnz++;
            }
        }
    }

    // Allocate memory
    csr.values = malloc(csr.nnz * sizeof(int));
    csr.col_index = malloc(csr.nnz * sizeof(int));
    csr.row_ptr = malloc((n + 1) * sizeof(int));

    if ((csr.nnz > 0 && (csr.values == NULL || csr.col_index == NULL))
        || csr.row_ptr == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    int index = 0;

    // Store nonzero values and their positions
    for (int i = 0; i < n; i++) {
        csr.row_ptr[i] = index;

        for (int j = 0; j < n; j++) {
            if (A[i][j] != 0) {
                csr.values[index] = A[i][j];
                csr.col_index[index] = j;
                index++;
            }
        }
    }

    csr.row_ptr[n] = index;

    return csr;
}

void free_csr(CSRMatrix *csr) {
    free(csr->values);
    free(csr->col_index);
    free(csr->row_ptr);
}


void load_matrix(const char *filename, int n, int matrix[n][n]) {
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        fprintf(stderr, "Error opening file: %s\n", filename);
        exit(1);
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (fscanf(file, "%d", &matrix[i][j]) != 1) {
                fprintf(stderr, "Error reading matrix\n");
                fclose(file);
                exit(1);
            }

            if (j < n - 1) {
                fscanf(file, ",");
            }
        }
    }

    fclose(file);
}

void multiply_csr(CSRMatrix *A, CSRMatrix *B, int C[A->n][A->n]) {
    int n = A->n;

    // Initialize result matrix
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
        }
    }

    // Multiply using nonzero elements
    for (int i = 0; i < n; i++) {
        for (int a = A->row_ptr[i]; a < A->row_ptr[i + 1]; a++) {
            int k = A->col_index[a];
            int value = A->values[a];

            for (int b = B->row_ptr[k]; b < B->row_ptr[k + 1]; b++) {
                int j = B->col_index[b];

                C[i][j] += value * B->values[b];
            }
        }
    }
}


void multiply_dense(int n, int A[n][n], int B[n][n], int C[n][n]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
        }
    }

    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            for (int j = 0; j < n; j++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}


double current_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    return ts.tv_sec + ts.tv_nsec / 1000000000.0;
}

int compare_doubles(const void *a, const void *b) {
    double x = *(const double *)a;
    double y = *(const double *)b;

    return (x > y) - (x < y);
}

void print_statistics(const char *method, double times[5]) {
    double sorted[5];

    for (int i = 0; i < 5; i++) {
        sorted[i] = times[i];
    }

    qsort(sorted, 5, sizeof(double), compare_doubles);

    printf("%s median: %.6f ms\n", method, sorted[2] * 1000);
    printf("%s IQR: %.6f ms\n",
           method, (sorted[3] - sorted[1]) * 1000);
}

static volatile int result_sink;


int run_correctness_tests(void) {
    int passed = 1;

    int A[3][3] = {
        {1, 0, 2},
        {0, 0, 0},
        {3, 0, 4}
    };

    int B[3][3] = {
        {0, 5, 0},
        {0, 0, 0},
        {6, 0, 7}
    };

    int expected[3][3] = {
        {12, 5, 14},
        {0, 0, 0},
        {24, 15, 28}
    };

    int C[3][3];

    CSRMatrix csrA = dense_to_csr(3, A);
    CSRMatrix csrB = dense_to_csr(3, B);

    multiply_csr(&csrA, &csrB, C);

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (C[i][j] != expected[i][j]) {
                passed = 0;
            }
        }
    }

    printf("%s sparse multiplication with empty rows\n",
           passed ? "PASS" : "FAIL");

    free_csr(&csrA);
    free_csr(&csrB);

    // Test multiplication by a zero matrix
    int zero[3][3] = {{0}};

    CSRMatrix csrZero = dense_to_csr(3, zero);
    csrA = dense_to_csr(3, A);

    multiply_csr(&csrA, &csrZero, C);

    int zero_passed = 1;

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (C[i][j] != 0) {
                zero_passed = 0;
            }
        }
    }

    printf("%s sparse multiplication by zero\n",
           zero_passed ? "PASS" : "FAIL");

    free_csr(&csrA);
    free_csr(&csrZero);

    if (passed && zero_passed) {
        printf("All CSR correctness tests passed\n");
    }

    return passed && zero_passed;
}




int main(int argc, char *argv[]) {
    int sizes[] = {100, 300, 500, 750, 1000};
    int sparsities[] = {50, 90, 95, 99};
    int repetitions = 5;


int selected_size = 0;
int selected_sparsity = 0;

if (argc == 3) {
    selected_size = atoi(argv[1]);
    selected_sparsity = atoi(argv[2]);

    int valid_size = 0;
    int valid_sparsity = 0;

    for (int i = 0; i < 5; i++) {
        if (sizes[i] == selected_size) {
            valid_size = 1;
        }
    }

    for (int i = 0; i < 4; i++) {
        if (sparsities[i] == selected_sparsity) {
            valid_sparsity = 1;
        }
    }

    if (!valid_size || !valid_sparsity) {
        fprintf(stderr, "Invalid size or sparsity\n");
        return 1;
    }
    } else if (argc != 1) {
        fprintf(stderr, "Usage: %s [size sparsity]\n", argv[0]);
        return 1;
    }


    if (!run_correctness_tests()) {
        return 1;
    }

    FILE *csv = fopen("results/sparse_times.csv", "w");
    FILE *memory_csv = fopen("results/sparse_memory.csv", "w");

    if (csv == NULL || memory_csv == NULL) {
        fprintf(stderr, "Error creating CSV files\n");
        if (csv) fclose(csv);
        if (memory_csv) fclose(memory_csv);
        return 1;
    }

    fprintf(csv,
            "size,sparsity,repetition,batch_size,"
            "dense_time_seconds,csr_time_seconds,"
            "conversion_time_seconds,nnz_A,nnz_B,nnz_C\n");

    fprintf(memory_csv,
            "size,sparsity,nnz_A,nnz_B,nnz_C,"
            "dense_storage_mib,csr_storage_mib\n");

    for (int s = 0; s < 5; s++) {
        int n = sizes[s];

        if (selected_size != 0 && n != selected_size) {
            continue;
        }

        for (int p = 0; p < 4; p++) {
            int sparsity = sparsities[p];

            if (selected_sparsity != 0 &&
                sparsity != selected_sparsity) {
                continue;
            }

        int batch_size = (n <= 100) ? 10 : 1;

            printf("\nMatrix size: %dx%d\n", n, n);
            printf("Sparsity: %d%%\n", sparsity);

            int (*A)[n] = malloc(sizeof(int[n][n]));
            int (*B)[n] = malloc(sizeof(int[n][n]));
            int (*C)[n] = malloc(sizeof(int[n][n]));
            int (*expected)[n] = malloc(sizeof(int[n][n]));

            if (!A || !B || !C || !expected) {
                fprintf(stderr, "Memory allocation failed\n");
                free(A);
                free(B);
                free(C);
                free(expected);
                fclose(csv);
                fclose(memory_csv);
                return 1;
            }

            char filename[100];

            snprintf(filename, sizeof(filename),
                     "data/sparse/A_%d_%d.csv", n, sparsity);
            load_matrix(filename, n, A);

            snprintf(filename, sizeof(filename),
                     "data/sparse/B_%d_%d.csv", n, sparsity);
            load_matrix(filename, n, B);

            CSRMatrix csrA = dense_to_csr(n, A);
            CSRMatrix csrB = dense_to_csr(n, B);

            // Validate both methods
            multiply_dense(n, A, B, expected);
            multiply_csr(&csrA, &csrB, C);

            int correct = 1;
            int nnzC = 0;

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (C[i][j] != expected[i][j]) {
                        correct = 0;
                    }

                    if (C[i][j] != 0) {
                        nnzC++;
                    }
                }
            }

            if (!correct) {
                fprintf(stderr, "CSR validation failed\n");
                free_csr(&csrA);
                free_csr(&csrB);
                free(A);
                free(B);
                free(C);
                free(expected);
                fclose(csv);
                fclose(memory_csv);
                return 1;
            }

            printf("PASS CSR vs dense validation\n");
            printf("NNZ A: %d, B: %d, C: %d\n",
                   csrA.nnz, csrB.nnz, nnzC);

            double dense_times[5];
            double csr_times[5];
            double conversion_times[5];

            // Warm-up (not measured)
            multiply_dense(n, A, B, expected);
            multiply_csr(&csrA, &csrB, C);
            result_sink = C[0][0];

            for (int rep = 0; rep < repetitions; rep++) {
                double start, end;

                // Alternate execution order
                for (int method = 0; method < 2; method++) {
                    int dense_first = (rep % 2 == 0);
                    int run_dense = (method == 0)
                                    ? dense_first : !dense_first;

                    start = current_time();

                    for (int b = 0; b < batch_size; b++) {
                        if (run_dense) {
                            multiply_dense(n, A, B, expected);
                            result_sink = expected[0][0];
                        } else {
                            multiply_csr(&csrA, &csrB, C);
                            result_sink = C[0][0];
                        }
                    }

                    end = current_time();

                    double elapsed =
                        (end - start) / batch_size;

                    if (run_dense) {
                        dense_times[rep] = elapsed;
                    } else {
                        csr_times[rep] = elapsed;
                    }
                }

                // Measure conversion separately
                start = current_time();

                CSRMatrix tempA = dense_to_csr(n, A);
                CSRMatrix tempB = dense_to_csr(n, B);

                end = current_time();

                conversion_times[rep] = end - start;

                free_csr(&tempA);
                free_csr(&tempB);

                fprintf(csv,
                        "%d,%d,%d,%d,%.9f,%.9f,%.9f,%d,%d,%d\n",
                        n, sparsity, rep + 1, batch_size,
                        dense_times[rep],
                        csr_times[rep],
                        conversion_times[rep],
                        csrA.nnz, csrB.nnz, nnzC);

                printf("Repetition %d: Dense %.4f ms, "
                       "CSR %.4f ms, Conversion %.4f ms\n",
                       rep + 1,
                       dense_times[rep] * 1000,
                       csr_times[rep] * 1000,
                       conversion_times[rep] * 1000);
            }

            print_statistics("Dense", dense_times);
            print_statistics("CSR", csr_times);
            print_statistics("Conversion", conversion_times);

            // Estimated matrix storage
            size_t dense_bytes =
                3 * (size_t)n * n * sizeof(int);

            size_t csr_bytes =
                2 * (size_t)(csrA.nnz + csrB.nnz) * sizeof(int)
                + 2 * (size_t)(n + 1) * sizeof(int)
                + (size_t)n * n * sizeof(int);

            double dense_mib =
                dense_bytes / (1024.0 * 1024.0);

            double csr_mib =
                csr_bytes / (1024.0 * 1024.0);

            fprintf(memory_csv,
                    "%d,%d,%d,%d,%d,%.6f,%.6f\n",
                    n, sparsity, csrA.nnz, csrB.nnz,
                    nnzC, dense_mib, csr_mib);

            printf("Dense storage: %.6f MiB\n", dense_mib);
            printf("CSR storage: %.6f MiB\n", csr_mib);

            fflush(csv);
            fflush(memory_csv);

            free_csr(&csrA);
            free_csr(&csrB);

            free(A);
            free(B);
            free(C);
            free(expected);
        }
    }

    fclose(csv);
    fclose(memory_csv);

    printf("\nAll sparse benchmarks completed\n");

    return 0;
}
