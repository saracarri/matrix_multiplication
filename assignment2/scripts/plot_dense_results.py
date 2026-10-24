
import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


methods = {
    "Baseline": "baseline_times.csv",
    "Reordered": "reordered_times.csv",
    "Blocked": "blocked_times.csv"
}

times = {}

for method, filename in methods.items():
    with open(RESULTS / filename, newline="") as file:
        times[method] = list(csv.DictReader(file))


with open(RESULTS / "dense_process_memory.csv", newline="") as file:
    memories = list(csv.DictReader(file))


sizes = [10, 50, 100, 200, 300, 500, 750, 1000]


def get_measurements(method, n):
    values = []

    for row in times[method]:
        if int(row["size"]) == n:
            values.append(float(row["time_seconds"]) * 1000)

    if len(values) != 5:
        raise ValueError(
            f"Expected five measurements for {method}, size {n}"
        )

    return sorted(values)


def median_ms(method, n):
    return median(get_measurements(method, n))


def iqr_ms(method, n):
    values = get_measurements(method, n)

    return values[3] - values[1]


# Compare execution times
plt.figure(figsize=(7, 4.5))

for method in methods:
    medians = []

    for n in sizes:
        medians.append(median_ms(method, n))

    plt.plot(sizes, medians, marker="o", label=method)

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Median execution time (ms)")
plt.title("Dense matrix multiplication performance")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "dense_execution_time.png", dpi=180)
plt.close()


# Calculate speedup relative to baseline
plt.figure(figsize=(7, 4.5))

for method in ["Reordered", "Blocked"]:
    speedups = []

    for n in sizes:
        baseline_time = median_ms("Baseline", n)
        optimized_time = median_ms(method, n)

        speedups.append(baseline_time / optimized_time)

    plt.plot(sizes, speedups, marker="o", label=method)

plt.axhline(1, linestyle="--", color="gray",
            label="No speedup")

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Speedup (Baseline / Optimized)")
plt.title("Dense matrix multiplication speedup")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "dense_speedup.png", dpi=180)
plt.close()


# Compare execution time variability
plt.figure(figsize=(7, 4.5))

for method in methods:
    iqrs = []

    for n in sizes:
        iqrs.append(iqr_ms(method, n))

    plt.plot(sizes, iqrs, marker="o", label=method)

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Interquartile range (ms)")
plt.title("Execution time variability")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "dense_variability.png", dpi=180)
plt.close()


# Compare peak process memory
plt.figure(figsize=(7, 4.5))

for method in methods:
    memory_values = []

    for n in sizes:
        matching = [
            float(row["peak_rss_mib"])
            for row in memories
            if row["method"] == method and int(row["size"]) == n
        ]

        if len(matching) != 1:
            raise ValueError(
                f"Missing memory measurement for {method}, size {n}"
            )

        memory_values.append(matching[0])

    plt.plot(sizes, memory_values, marker="o", label=method)

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Peak process RSS (MiB)")
plt.title("Dense matrix multiplication memory usage")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "dense_process_memory.png", dpi=180)
plt.close()


print(f"Saved 4 dense plots to {FIGURES}")
