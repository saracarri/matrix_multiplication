import time
import statistics
import csv
import tracemalloc


def matrix_multiplication(A, B, C):
    n = len(A)

    for i in range(n):
        for j in range(n):
            C[i][j] = 0

            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C


def load_matrix(filename):
    matrix = []

    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            matrix.append([int(value) for value in row])

    return matrix


def reference_multiplication(A, B):
    n = len(A)
    return [
        [sum(A[i][k] * B[k][j] for k in range(n))
         for j in range(n)]
        for i in range(n)
    ]


def benchmark(n, repetitions=5):
    A = load_matrix(f"data/A_{n}.csv")
    B = load_matrix(f"data/B_{n}.csv")
    C = [[0 for _ in range(n)] for _ in range(n)]

    # Warm-up (not measured)
    matrix_multiplication(A, B, C)

    expected = reference_multiplication(A, B)

    times = []

    for rep in range(repetitions):
        start = time.perf_counter()

        matrix_multiplication(A, B, C)

        end = time.perf_counter()

        assert C == expected, "Incorrect multiplication result"

        times.append(end - start)

    return times


def measure_memory(n):
    A = load_matrix(f"data/A_{n}.csv")
    B = load_matrix(f"data/B_{n}.csv")
    C = [[0 for _ in range(n)] for _ in range(n)]

    tracemalloc.start()

    matrix_multiplication(A, B, C)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return peak / (1024 * 1024)


if __name__ == "__main__":
    sizes = [10, 50, 100]

    with open("results/python_times.csv", "w", newline="") as time_file, \
         open("results/python_memory.csv", "w", newline="") as memory_file:

        time_writer = csv.writer(time_file)
        memory_writer = csv.writer(memory_file)

        time_writer.writerow(["language", "size", "repetition", "time_seconds"])
        memory_writer.writerow(["language", "size", "peak_memory_mib"])

        for n in sizes:
            times = benchmark(n)

            for rep, elapsed in enumerate(times, start=1):
                time_writer.writerow(["Python", n, rep, elapsed])

            median = statistics.median(times) * 1000

            sorted_times = sorted(times)
            q1 = sorted_times[1]
            q3 = sorted_times[3]
            iqr = (q3 - q1) * 1000

            memory = measure_memory(n)
            memory_writer.writerow(["Python", n, memory])

            print(f"Matrix size: {n}x{n}")
            print(f"Median: {median:.6f} ms")
            print(f"IQR: {iqr:.6f} ms")
            print(f"Peak memory: {memory:.4f} MiB")
            print()
