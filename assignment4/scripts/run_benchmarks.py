
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MPIEXEC = Path(
    r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
)

EXECUTABLE = ROOT / "c" / "distributed.exe"

SIZES = [100, 300, 500, 750, 1000]
PROCESSES = [1, 2, 4, 8]

RESULTS = ROOT / "results"
TIME_CSV = RESULTS / "distributed_times.csv"
MEMORY_CSV = RESULTS / "distributed_memory.csv"


def main():
    if not MPIEXEC.is_file():
        print("Error: mpiexec.exe was not found.")
        sys.exit(1)

    if not EXECUTABLE.is_file():
        print("Error: distributed.exe was not found.")
        sys.exit(1)

    RESULTS.mkdir(parents=True, exist_ok=True)

    # Avoid mixing previous measurements with this benchmark.
    if TIME_CSV.exists() or MEMORY_CSV.exists():
        print("Existing benchmark results detected.")
        print("Move or rename the current CSV files before running.")
        sys.exit(1)

    total = len(SIZES) * len(PROCESSES)
    completed = 0

    for n in SIZES:
        for processes in PROCESSES:
            completed += 1

            print(
                f"\n[{completed}/{total}] "
                f"n={n}, processes={processes}",
                flush=True,
            )

            command = [
                str(MPIEXEC),
                "-n",
                str(processes),
                str(EXECUTABLE),
                str(n),
            ]

            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            print(result.stdout)

            if result.returncode != 0:
                print(result.stderr)
                print("Benchmark failed.")
                sys.exit(1)

            if "Validation: PASS" not in result.stdout:
                print("Validation failed.")
                sys.exit(1)

    print("\nAll benchmarks completed successfully.")
    print(f"Timing results: {TIME_CSV}")
    print(f"Memory results: {MEMORY_CSV}")


if __name__ == "__main__":
    main()
