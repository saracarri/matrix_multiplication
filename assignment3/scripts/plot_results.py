
import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FIGURES.mkdir(exist_ok=True)

SIZES = [100, 300, 500, 750, 1000]
THREADS = [1, 2, 4, 8, 16, 22]

data = {}

with open(RESULTS / "performance_summary.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        method = row["method"]
        n = int(row["size"])
        threads = int(row["threads"])

        data[(method, n, threads)] = {
            "time": float(row["median_ms"]),
            "speedup": float(row["speedup"]),
            "efficiency": float(row["efficiency"])
        }


# Figure 1: Execution time

plt.figure(figsize=(9, 5))

sequential = [
    data[("sequential", n, 1)]["time"]
    for n in SIZES
]

plt.plot(SIZES, sequential, marker="o", label="Sequential")

for threads in THREADS:
    times = [
        data[("parallel", n, threads)]["time"]
        for n in SIZES
    ]

    plt.plot(SIZES, times, marker="o", label=f"{threads} threads")

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Median execution time (ms)")
plt.title("Sequential vs parallel matrix multiplication")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(FIGURES / "execution_time.png", dpi=300)
plt.close()


# Figure 2: Speedup

plt.figure(figsize=(9, 5))

for n in SIZES:
    speedups = [
        data[("parallel", n, p)]["speedup"]
        for p in THREADS
    ]

    plt.plot(THREADS, speedups, marker="o", label=f"n = {n}")

plt.plot(THREADS, THREADS, "--", color="black", label="Ideal speedup")

plt.xlabel("Number of threads")
plt.ylabel("Speedup (Tseq / Tp)")
plt.title("Parallel speedup")
plt.xticks(THREADS)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(FIGURES / "speedup.png", dpi=300)
plt.close()


# Figure 3: Efficiency

plt.figure(figsize=(9, 5))

for n in SIZES:
    efficiencies = [
        data[("parallel", n, p)]["efficiency"] * 100
        for p in THREADS
    ]

    plt.plot(THREADS, efficiencies, marker="o", label=f"n = {n}")

plt.axhline(100, linestyle="--", color="black", label="100% efficiency")

plt.xlabel("Number of threads")
plt.ylabel("Parallel efficiency (%)")
plt.title("Parallel efficiency")
plt.xticks(THREADS)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(FIGURES / "efficiency.png", dpi=300)
plt.close()

# Figure 4: Process memory (RSS)

memory_data = {}

with open(RESULTS / "process_memory.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        method = row["method"]
        n = int(row["size"])
        threads = int(row["threads"])
        rss = float(row["peak_rss_mib"])

        memory_data[(method, n, threads)] = rss

plt.figure(figsize=(9, 5))

sequential_memory = [
    memory_data[("sequential", n, 1)]
    for n in SIZES
]

plt.plot(SIZES, sequential_memory, marker="o", label="Sequential")

for threads in THREADS:
    values = [
        memory_data[("parallel", n, threads)]
        for n in SIZES
    ]

    plt.plot(SIZES, values, marker="o", label=f"{threads} threads")

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Peak process RSS (MiB)")
plt.title("Process memory usage")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(FIGURES / "memory_usage.png", dpi=300)
plt.close()

print("Performance figures generated successfully.")
