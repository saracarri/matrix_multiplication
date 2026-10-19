
import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"

FIGURES.mkdir(exist_ok=True)

files = {
    "Python": "python_times.csv",
    "Java": "java_times.csv",
    "C": "c_times.csv"
}

sizes = [10, 50, 100, 200, 300]
medians = {}

# Read execution times and calculate medians
for language, filename in files.items():
    measurements = {}

    with open(RESULTS / filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            n = int(row["size"])
            elapsed = float(row["time_seconds"]) * 1000

            measurements.setdefault(n, []).append(elapsed)

    medians[language] = [
        statistics.median(measurements[n])
        for n in sizes
    ]

# Figure 1: Execution time
plt.figure(figsize=(8, 5))

for language, values in medians.items():
    plt.plot(sizes, values, marker="o", label=language)

plt.xlabel("Matrix size (n)")
plt.ylabel("Median execution time (ms)")
plt.title("Matrix Multiplication Execution Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIGURES / "execution_time.png", dpi=300)
plt.close()

# Figure 2: Logarithmic execution time
plt.figure(figsize=(8, 5))

for language, values in medians.items():
    plt.plot(sizes, values, marker="o", label=language)

plt.yscale("log")
plt.xlabel("Matrix size (n)")
plt.ylabel("Median execution time (ms, log scale)")
plt.title("Matrix Multiplication Execution Time (Log Scale)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIGURES / "execution_time_log.png", dpi=300)
plt.close()

# Figure 3: Peak RSS memory
memory = {}

with open(RESULTS / "process_memory_by_size.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        language = row["language"]
        n = int(row["size"])
        rss = float(row["peak_rss_mib"])

        memory.setdefault(language, {})[n] = rss

plt.figure(figsize=(8, 5))

for language, values in memory.items():
    plt.plot(
        sizes,
        [values[n] for n in sizes],
        marker="o",
        label=language
    )

plt.xlabel("Matrix size (n)")
plt.ylabel("Observed peak RSS (MiB)")
plt.title("Process Memory Usage")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(FIGURES / "memory_usage.png", dpi=300)
plt.close()

print("Figures generated successfully.")
