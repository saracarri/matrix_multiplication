import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.Arrays;

public class MatrixMultiplication {

    private static volatile long checksumSink;

    public static void matrixMultiplication(int[][] A, int[][] B, int[][] C) {
        int n = A.length;

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                C[i][j] = 0;

                for (int k = 0; k < n; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
    }


    public static int[][] loadMatrix(String filename, int n) throws IOException {
        int[][] matrix = new int[n][n];

        BufferedReader reader = new BufferedReader(new FileReader(filename));

        for (int i = 0; i < n; i++) {
            String line = reader.readLine();
            String[] values = line.split(",");

            for (int j = 0; j < n; j++) {
                matrix[i][j] = Integer.parseInt(values[j]);
            }
        }

        reader.close();
        return matrix;
    }


public static boolean validateMatrix(int[][] C, int n) throws IOException {
    int[][] expected = loadMatrix("data/expected/C_" + n + ".csv", n);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (C[i][j] != expected[i][j]) {
                return false;
            }
        }
    }

    return true;
}

    public static long matrixChecksum(int[][] matrix) {
        long sum = 0;

        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                sum += matrix[i][j];
            }
        }

        return sum;
    }


    
    public static double[] benchmark(int n, int repetitions) throws IOException {
        int[][] A = loadMatrix("data/A_" + n + ".csv", n);
        int[][] B = loadMatrix("data/B_" + n + ".csv", n);
        int[][] C = new int[n][n];

        // Warm-up (not measured)
        for (int i = 0; i < 10; i++) {
            matrixMultiplication(A, B, C);
            checksumSink = matrixChecksum(C);
        }

        double[] times = new double[repetitions];

        for (int rep = 0; rep < repetitions; rep++) {
            long start = System.nanoTime();

            matrixMultiplication(A, B, C);

            long end = System.nanoTime();

            checksumSink = matrixChecksum(C);
            times[rep] = (end - start) / 1_000_000_000.0;
        }
        if (!validateMatrix(C, n)) {
            throw new IllegalStateException("Incorrect result for size " + n);
        }

        System.out.println("Validation passed for " + n + "x" + n);

        return times;
    }


    
    public static double measureMemory(int n) {
        long totalBytes = 3L * n * n * Integer.BYTES;

        return totalBytes / (1024.0 * 1024.0);
    }

        public static void checkResult(String name, int[][] actual, int[][] expected) {
        if (!Arrays.deepEquals(actual, expected)) {
            throw new IllegalStateException("Correctness test failed: " + name);
        }

        System.out.println("PASS " + name);
    }

    public static void runCorrectnessTests() {
        int[][] a = {{1, 2}, {3, 4}};
        int[][] b = {{5, 6}, {7, 8}};
        int[][] result = new int[2][2];
        matrixMultiplication(a, b, result);
        checkResult("2x2 known result", result, new int[][]{{19, 22}, {43, 50}});

        int n = 4;
        int[][] m = new int[n][n];
        int[][] identity = new int[n][n];
        int[][] zero = new int[n][n];

        for (int i = 0; i < n; i++) {
            identity[i][i] = 1;

            for (int j = 0; j < n; j++) {
                m[i][j] = i * n + j + 1;
            }
        }

        result = new int[n][n];
        matrixMultiplication(m, identity, result);
        checkResult("A x I = A", result, m);

        result = new int[n][n];
        matrixMultiplication(identity, m, result);
        checkResult("I x A = A", result, m);

        result = new int[n][n];
        for (int[] row : result) {
            Arrays.fill(row, 7);
        }
        matrixMultiplication(m, zero, result);
        checkResult("A x 0 = 0", result, zero);

        result = new int[n][n];
        matrixMultiplication(zero, m, result);
        checkResult("0 x A = 0", result, zero);

        System.out.println("All Java correctness tests passed");
    }

    public static void main(String[] args) throws IOException {
        if (args.length > 0 && args[0].equals("--test")) {
            runCorrectnessTests();
            return;
        }
        int[] sizes = args.length > 0
            ? new int[]{Integer.parseInt(args[0])}
            : new int[]{10, 50, 100, 200, 300};

        PrintWriter writer = new PrintWriter(new FileWriter("results/java_times.csv"));
        writer.println("language,size,repetition,time_seconds");
        PrintWriter memoryWriter = new PrintWriter(
            new FileWriter("results/java_memory.csv")
        );
        memoryWriter.println("language,size,estimated_array_storage_mib");
        for (int n : sizes) {
            double[] times = benchmark(n, 5);
            
            for (int rep = 0; rep < times.length; rep++) {
                writer.println("Java," + n + "," + (rep + 1) + "," + times[rep]);
            }

            double[] sortedTimes = times.clone();
            Arrays.sort(sortedTimes);

            double median = sortedTimes[2] * 1000;
            double iqr = (sortedTimes[3] - sortedTimes[1]) * 1000;

            double memory = measureMemory(n);
            memoryWriter.println("Java," + n + "," + memory);

            System.out.println("Matrix size: " + n + "x" + n);
            System.out.printf("Median: %.6f ms%n", median);
            System.out.printf("IQR: %.6f ms%n", iqr);
            System.out.printf("Estimated array storage: %.6f MiB%n", memory);
            System.out.println();
        }

        writer.close();
        memoryWriter.close();
    }

}
