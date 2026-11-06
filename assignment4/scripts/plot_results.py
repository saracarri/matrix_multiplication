
import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)

TIME_CSV = RESULTS / "distributed_times.csv"
MEMORY_CSV = RESULTS / "distributed_memory.csv"


def load_times():
    measurements = {}

    with open(TIME_CSV, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            n = int(row["n"])
            processes = int(row["processes"])
            total = float(row["total_ms"])

            key = (n, processes)
            measurements.setdefault(key, []).append(total)

    return {
        key: median(values)
        for key, values in measurements.items()
    }


def load_memory():
    measurements = {}

    with open(MEMORY_CSV, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            n = int(row["n"])
            processes = int(row["processes"])
            memory = float(row["sum_worker_peak_mib"])

            key = (n, processes)
            measurements.setdefault(key, []).append(memory)

    return {
        key: median(values)
        for key, values in measurements.items()
    }


def plot_execution_time(times, sizes, processes):
    plt.figure(figsize=(8, 5))

    for p in processes:
        x = [n for n in sizes if (n, p) in times]
        y = [times[(n, p)] for n in x]

        plt.plot(x, y, marker="o", label=f"{p} processes")

    plt.xlabel("Matrix size (n)")
    plt.ylabel("Execution time (ms)")
    plt.title("MPI Matrix Multiplication: Execution Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES / "execution_time.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def plot_speedup(times, sizes, processes):
    plt.figure(figsize=(8, 5))

    for n in sizes:
        if (n, 1) not in times:
            continue

        baseline = times[(n, 1)]
        x = [p for p in processes if (n, p) in times]
        y = [baseline / times[(n, p)] for p in x]

        plt.plot(x, y, marker="o", label=f"n={n}")

    plt.plot(
        processes,
        processes,
        linestyle="--",
        color="black",
        label="Ideal speedup",
    )

    plt.xlabel("Number of MPI processes")
    plt.ylabel("Speedup")
    plt.title("MPI Matrix Multiplication: Speedup")
    plt.xticks(processes)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES / "speedup.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def plot_efficiency(times, sizes, processes):
    plt.figure(figsize=(8, 5))

    for n in sizes:
        if (n, 1) not in times:
            continue

        baseline = times[(n, 1)]
        x = [p for p in processes if (n, p) in times]

        y = [
            (baseline / times[(n, p)]) / p * 100
            for p in x
        ]

        plt.plot(x, y, marker="o", label=f"n={n}")

    plt.axhline(
        100,
        linestyle="--",
        color="black",
        label="Ideal efficiency",
    )

    plt.xlabel("Number of MPI processes")
    plt.ylabel("Efficiency (%)")
    plt.title("MPI Matrix Multiplication: Efficiency")
    plt.xticks(processes)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES / "efficiency.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def plot_memory(memory, sizes, processes):
    plt.figure(figsize=(8, 5))

    for n in sizes:
        x = [p for p in processes if (n, p) in memory]
        y = [memory[(n, p)] for p in x]

        plt.plot(x, y, marker="o", label=f"n={n}")

    plt.xlabel("Number of MPI processes")
    plt.ylabel("Sum of worker peak memory (MiB)")
    plt.title("MPI Matrix Multiplication: Memory Usage")
    plt.xticks(processes)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES / "memory_usage.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def main():
    times = load_times()
    memory = load_memory()

    sizes = sorted({n for n, p in times})
    processes = sorted({p for n, p in times})

    plot_execution_time(times, sizes, processes)
    plot_speedup(times, sizes, processes)
    plot_efficiency(times, sizes, processes)
    plot_memory(memory, sizes, processes)

    print("All figures generated successfully.")
    print(f"Figures saved in: {FIGURES}")


if __name__ == "__main__":
    main()
