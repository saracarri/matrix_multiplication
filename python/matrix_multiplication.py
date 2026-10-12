import random
import time
import statistics
import csv
import tracemalloc

def matrix_multiplication(A, B):
    n = len(A)
    C = []

    for i in range(n):
        fila = []
        for j in range(n):
            fila.append(0)
        C.append(fila)

    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C


def generate_matrix(n, seed):
    rng = random.Random(seed)
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            row.append(rng.randint(0, 9))
        matrix.append(row)

    return matrix


def reference_multiplication(A, B):
    n = len(A)
    return [
        [sum(A[i][k] * B[k][j] for k in range(n))
         for j in range(n)]
        for i in range(n)
    ]



def benchmark(n, repetitions=5):
    A = generate_matrix(n, 42)
    B = generate_matrix(n, 43)

    # Warm-up (not measured)
    matrix_multiplication(A, B)

    expected = reference_multiplication(A, B)

    times = []

    for rep in range(repetitions):
        start = time.perf_counter()

        C = matrix_multiplication(A, B)

        end = time.perf_counter()

        assert C == expected, "Incorrect multiplication result"

        times.append(end - start)

    return times


def measure_memory(n):
    A = generate_matrix(n, 42)
    B = generate_matrix(n, 43)

    tracemalloc.start()

    C = matrix_multiplication(A, B)

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
