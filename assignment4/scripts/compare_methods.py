
import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT3 = ROOT.parent / "assignment3"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)

SIZES = [100, 300, 500, 750, 1000]
WORKERS = [4, 8]


def load_assignment3():
    results = {}

    path = ASSIGNMENT3 / "results" / "performance_summary.csv"

    with open(path, newline="") as file:
        for row in csv.DictReader(file):
            n = int(row["size"])
            threads = int(row["threads"])
            method = row["method"]

            if n in SIZES:
                results[(method, n, threads)] = float(
                    row["median_ms"]
                )

    return results


def load_mpi():
    samples = {}

    path = RESULTS / "distributed_times.csv"

    with open(path, newline="") as file:
        for row in csv.DictReader(file):
            n = int(row["n"])
            processes = int(row["processes"])

            if n in SIZES:
                samples.setdefault((n, processes), []).append(
                    float(row["total_ms"])
                )

    return {
        key: median(values)
        for key, values in samples.items()
    }


def main():
    previous = load_assignment3()
    mpi = load_mpi()

    series = {
        "Sequential": [
            previous[("sequential", n, 1)] for n in SIZES
        ],
        "OpenMP (4 threads)": [
            previous[("parallel", n, 4)] for n in SIZES
        ],
        "OpenMP (8 threads)": [
            previous[("parallel", n, 8)] for n in SIZES
        ],
        "MPI (4 processes)": [
            mpi[(n, 4)] for n in SIZES
        ],
        "MPI (8 processes)": [
            mpi[(n, 8)] for n in SIZES
        ],
    }

    # Save comparative table
    output = RESULTS / "methods_comparison.csv"

    with open(output, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["n", *series.keys()])

        for i, n in enumerate(SIZES):
            writer.writerow([
                n,
                *[f"{values[i]:.6f}"
                  for values in series.values()]
            ])

    # Plot execution time
    plt.figure(figsize=(9, 5.5))

    for method, values in series.items():
        plt.plot(SIZES, values, marker="o", label=method)

    plt.xlabel("Matrix size (n)")
    plt.ylabel("Execution time (ms)")
    plt.title("Sequential, OpenMP and MPI: Execution Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES / "methods_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print("Comparison completed successfully.")
    print(f"Results: {output}")
    print(f"Figure: {FIGURES / 'methods_comparison.png'}")


if __name__ == "__main__":
    main()
