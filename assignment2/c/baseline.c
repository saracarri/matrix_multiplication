#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <string.h>

#define TEST_N 4

void matrix_multiplication(int n, int A[n][n], int B[n][n], int C[n][n]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;

            for (int k = 0; k < n; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

void load_matrix(const char *filename, int n, int matrix[n][n]) {
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        printf("Error opening file: %s\n", filename);
        exit(1);
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (fscanf(file, "%d", &matrix[i][j]) != 1) {
                printf("Error reading matrix\n");
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

long long matrix_checksum(int n, int matrix[n][n]) {
    long long sum = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            sum += matrix[i][j];
        }
    }

    return sum;
}


int validate_matrix(int n, int C[n][n]) {
    int (*expected)[n] = malloc(sizeof(int[n][n]));

    if (expected == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    char filename[100];
    if (n <= 300) {
        snprintf(filename, sizeof(filename),
                "../assignment1/data/expected/C_%d.csv", n);
    } else {
        snprintf(filename, sizeof(filename),
                "data/expected/C_%d.csv", n);
    }

    load_matrix(filename, n, expected);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (C[i][j] != expected[i][j]) {
                free(expected);
                return 0;
            }
        }
    }

    free(expected);
    return 1;
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

static volatile long long checksum_sink;

void benchmark(int n, int repetitions, FILE *csv) {
    double times[5];

    int (*A)[n] = malloc(sizeof(int[n][n]));
    int (*B)[n] = malloc(sizeof(int[n][n]));
    int (*C)[n] = malloc(sizeof(int[n][n]));

    if (A == NULL || B == NULL || C == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(A);
        free(B);
        free(C);
        exit(1);
    }

    char filename[100];

    if (n <= 300) {
        snprintf(filename, sizeof(filename),
                "../assignment1/data/A_%d.csv", n);
    } else {
        snprintf(filename, sizeof(filename),
                "data/A_%d.csv", n);
    }
    load_matrix(filename, n, A);

    if (n <= 300) {
        snprintf(filename, sizeof(filename),
                "../assignment1/data/B_%d.csv", n);
    } else {
        snprintf(filename, sizeof(filename),
                "data/B_%d.csv", n);
    }
    load_matrix(filename, n, B);

    // Warm-up (not measured)
    matrix_multiplication(n, A, B, C);
    checksum_sink = matrix_checksum(n, C);

    for (int rep = 1; rep <= repetitions; rep++) {
        
        int batch_size = (n <= 10) ? 1000 : 1;

        double start = current_time();

        for (int b = 0; b < batch_size; b++) {
            matrix_multiplication(n, A, B, C);
            checksum_sink = C[0][0];
        }

        double end = current_time();
        double elapsed = (end - start) / batch_size;


        times[rep - 1] = elapsed;

        fprintf(csv, "C,%d,%d,%d,%.9f\n", n, rep, batch_size, elapsed);
        printf("Repetition %d: %.6f ms\n", rep, elapsed * 1000);
    }

    if (!validate_matrix(n, C)) {
        fprintf(stderr, "Incorrect result for size %d\n", n);
        free(A);
        free(B);
        free(C);
        exit(1);
    }

    printf("Validation passed for %dx%d\n", n, n);
    qsort(times, 5, sizeof(double), compare_doubles);

    double median = times[2] * 1000;
    double iqr = (times[3] - times[1]) * 1000;

    printf("Median: %.6f ms\n", median);
    printf("IQR: %.6f ms\n", iqr);

    free(A);
    free(B);
    free(C);
}

double measure_memory(int n) {
    size_t total_bytes = 3 * (size_t)n * n * sizeof(int);

    return total_bytes / (1024.0 * 1024.0);
}

int check_result(const char *name, int n, int C[n][n], int expected[n][n]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (C[i][j] != expected[i][j]) {
                printf("FAIL %s\n", name);
                return 0;
            }
        }
    }

    printf("PASS %s\n", name);
    return 1;
}

int run_correctness_tests(void) {
    int passed = 1;

    // 2x2 case with a result calculated by hand
    int a[2][2] = {{1, 2}, {3, 4}};
    int b[2][2] = {{5, 6}, {7, 8}};
    int known[2][2] = {{19, 22}, {43, 50}};
    int result2[2][2];

    matrix_multiplication(2, a, b, result2);
    passed &= check_result("2x2 known result", 2, result2, known);

    int m[TEST_N][TEST_N];
    int identity[TEST_N][TEST_N];
    int zero[TEST_N][TEST_N];
    int result[TEST_N][TEST_N];

    for (int i = 0; i < TEST_N; i++) {
        for (int j = 0; j < TEST_N; j++) {
            m[i][j] = i * TEST_N + j + 1;
            identity[i][j] = (i == j);
            zero[i][j] = 0;
        }
    }

    matrix_multiplication(TEST_N, m, identity, result);
    passed &= check_result("A x I = A", TEST_N, result, m);

    matrix_multiplication(TEST_N, identity, m, result);
    passed &= check_result("I x A = A", TEST_N, result, m);

    // result still holds non-zero values, so this also checks that it is reset
    matrix_multiplication(TEST_N, m, zero, result);
    passed &= check_result("A x 0 = 0", TEST_N, result, zero);

    matrix_multiplication(TEST_N, zero, m, result);
    passed &= check_result("0 x A = 0", TEST_N, result, zero);

    if (passed) {
        printf("All C correctness tests passed\n");
    }

    return passed;
}

int main(int argc, char *argv[]) {
    int sizes[] = {10, 50, 100, 200, 300, 500, 750, 1000};
    int count = sizeof(sizes) / sizeof(sizes[0]);

    if (argc == 3 && strcmp(argv[1], "--memory") == 0) {
    int n = atoi(argv[2]);

    if (n != 10 && n != 50 && n != 100 &&
        n != 200 && n != 300 && n != 500 &&
        n != 750 && n != 1000) {
        fprintf(stderr, "Invalid matrix size\n");
        return 1;
    }

    int (*A)[n] = malloc(sizeof(int[n][n]));
    int (*B)[n] = malloc(sizeof(int[n][n]));
    int (*C)[n] = malloc(sizeof(int[n][n]));

    if (A == NULL || B == NULL || C == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(A);
        free(B);
        free(C);
        return 1;
    }

    char filename[100];

    if (n <= 300) {
        snprintf(filename, sizeof(filename),
                 "../assignment1/data/A_%d.csv", n);
    } else {
        snprintf(filename, sizeof(filename),
                 "data/A_%d.csv", n);
    }
    load_matrix(filename, n, A);

    if (n <= 300) {
        snprintf(filename, sizeof(filename),
                 "../assignment1/data/B_%d.csv", n);
    } else {
        snprintf(filename, sizeof(filename),
                 "data/B_%d.csv", n);
    }
    load_matrix(filename, n, B);

    matrix_multiplication(n, A, B, C);
    checksum_sink = matrix_checksum(n, C);

    printf("Memory run completed for %dx%d\n", n, n);

    free(A);
    free(B);
    free(C);

    return 0;
}
    if (argc > 1 && strcmp(argv[1], "--test") == 0) {
        return run_correctness_tests() ? 0 : 1;
    }

    if (argc > 1) {
        int n = atoi(argv[1]);

        if (n != 10 && n != 50 && n != 100 &&
            n != 200 && n != 300 && n != 500 &&
            n != 750 && n != 1000) {
            fprintf(stderr, "Invalid matrix size\n");
            return 1;
        }

        sizes[0] = n;
        count = 1;
    }

    FILE *csv = fopen("results/baseline_times.csv", "w");

    if (csv == NULL) {
        fprintf(stderr, "Error creating CSV file\n");
        return 1;
    }

    FILE *memory_csv = fopen("results/baseline_memory.csv", "w");

    if (memory_csv == NULL) {
        fprintf(stderr, "Error creating memory CSV\n");
        fclose(csv);
        return 1;
    }

    fprintf(csv, "language,size,repetition,batch_size,time_seconds\n");
    fprintf(memory_csv, "language,size,estimated_array_storage_mib\n");

    for (int i = 0; i < count; i++) {
        int n = sizes[i];

        printf("Matrix size: %dx%d\n", n, n);

        benchmark(n, 5, csv);

        double memory = measure_memory(n);

        fprintf(memory_csv, "C,%d,%.6f\n", n, memory);
        printf("Estimated array storage: %.6f MiB\n", memory);
        printf("\n");
    }

    fclose(csv);
    fclose(memory_csv);

    return 0;
}

