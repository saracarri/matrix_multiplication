
import csv
import subprocess
import sys
import time
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]

MPIEXEC = Path(
    r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
)

EXECUTABLE = ROOT / "c" / "distributed.exe"
RESULTS = ROOT / "results" / "distributed_end_to_end.csv"

SIZES = [100, 300, 500, 750, 1000]
PROCESSES = [1, 2, 4, 8]

WARMUP_RUNS = 1
REPETITIONS = 5


def summarize(values):
    sorted_values = sorted(values)

    median_value = median(sorted_values)
    iqr = sorted_values[3] - sorted_values[1]

    return median_value, iqr


def measure(n, processes):
    command = [
        str(MPIEXEC),
        "-n",
        str(processes),
        str(EXECUTABLE),
        str(n),
        "--no-save",
    ]

    start = time.perf_counter()

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(
            f"MPI failed: n={n}, processes={processes}"
        )

    if "Validation: PASS" not in result.stdout:
        raise RuntimeError(
            f"Validation failed: n={n}, processes={processes}"
        )

    return elapsed_ms


def main():
    if not MPIEXEC.is_file():
        sys.exit("Error: mpiexec.exe was not found.")

    if not EXECUTABLE.is_file():
        sys.exit("Error: distributed.exe was not found.")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    if RESULTS.exists():
        sys.exit(
            "Results CSV already exists. "
            "Move or rename it before running a new benchmark."
        )

    total = len(SIZES) * len(PROCESSES)
    completed = 0

    with open(RESULTS, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "n",
            "processes",
            "repetition",
            "end_to_end_ms",
        ])

        for n in SIZES:
            for processes in PROCESSES:
                completed += 1

                print(
                    f"\n[{completed}/{total}] "
                    f"n={n}, processes={processes}",
                    flush=True,
                )

                # Warm-up: excluded from results
                for _ in range(WARMUP_RUNS):
                    measure(n, processes)

                samples = []

                for repetition in range(1, REPETITIONS + 1):
                    elapsed = measure(n, processes)
                    samples.append(elapsed)

                    writer.writerow([
                        n,
                        processes,
                        repetition,
                        f"{elapsed:.6f}",
                    ])
                    file.flush()

                med, iqr = summarize(samples)

                print(
                    f"Median: {med:.2f} ms "
                    f"(IQR: {iqr:.2f} ms)"
                )

    print("\nAll end-to-end benchmarks completed successfully.")
    print(f"Results saved in: {RESULTS}")


if __name__ == "__main__":
    main()
