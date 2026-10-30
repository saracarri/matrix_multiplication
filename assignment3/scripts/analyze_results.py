
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SIZES = [100, 300, 500, 750, 1000]
THREAD_COUNTS = [1, 2, 4, 8, 16, 22]


def load_times(filename):
    data = {}

    with open(RESULTS / filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            n = int(row["size"])
            elapsed = float(row["time_seconds"]) * 1000
            data.setdefault(n, []).append(elapsed)

    return data


def median_iqr(values):
    ordered = sorted(values)
    median = statistics.median(ordered)
    iqr = ordered[3] - ordered[1]
    return median, iqr


def main():
    sequential = load_times("sequential_times.csv")

    output = RESULTS / "performance_summary.csv"

    with open(output, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "method", "size", "threads", "median_ms",
            "iqr_ms", "speedup", "efficiency"
        ])

        baseline = {}

        for n in SIZES:
            median, iqr = median_iqr(sequential[n])
            baseline[n] = median

            writer.writerow([
                "sequential", n, 1,
                f"{median:.6f}", f"{iqr:.6f}",
                "1.000000", "1.000000"
            ])

        for threads in THREAD_COUNTS:
            parallel = load_times(
                f"parallel_{threads}_threads_times.csv"
            )

            for n in SIZES:
                median, iqr = median_iqr(parallel[n])

                speedup = baseline[n] / median
                efficiency = speedup / threads

                writer.writerow([
                    "parallel", n, threads,
                    f"{median:.6f}", f"{iqr:.6f}",
                    f"{speedup:.6f}", f"{efficiency:.6f}"
                ])

                print(
                    f"n={n}, threads={threads}: "
                    f"median={median:.3f} ms, "
                    f"speedup={speedup:.2f}, "
                    f"efficiency={efficiency:.2%}"
                )

    print(f"\nResults saved to {output}")


if __name__ == "__main__":
    main()
