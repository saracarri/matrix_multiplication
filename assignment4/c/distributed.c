
#include <stdio.h>
#include <mpi.h>

#define N 4

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (N % size != 0) {
        if (rank == 0) {
            fprintf(stderr, "Number of processes must divide N\n");
        }
        MPI_Finalize();
        return 1;
    }

    int A[N][N];
    int B[N][N];
    int C[N][N];

    int rows = N / size;
    int local_A[rows][N];
    int local_C[rows][N];

    if (rank == 0) {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                A[i][j] = i * N + j + 1;
                B[i][j] = (i == j) ? 1 : 0;
            }
        }
    }

    // Distribute matrix B to every process
    MPI_Bcast(B, N * N, MPI_INT, 0, MPI_COMM_WORLD);

    // Distribute rows of matrix A
    MPI_Scatter(A, rows * N, MPI_INT,
                local_A, rows * N, MPI_INT,
                0, MPI_COMM_WORLD);

    // Compute local matrix multiplication
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < N; j++) {
            local_C[i][j] = 0;
        }

        for (int k = 0; k < N; k++) {
            for (int j = 0; j < N; j++) {
                local_C[i][j] += local_A[i][k] * B[k][j];
            }
        }
    }

    // Collect results in process 0
    MPI_Gather(local_C, rows * N, MPI_INT,
               C, rows * N, MPI_INT,
               0, MPI_COMM_WORLD);

    if (rank == 0) {
        int correct = 1;

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (C[i][j] != A[i][j]) {
                    correct = 0;
                }
            }
        }

        printf("Validation: %s\n",
               correct ? "PASS" : "FAIL");
    }

    MPI_Finalize();
    return 0;
}
