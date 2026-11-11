
import csv
import subprocess
import sys
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
EXECUTABLE = ROOT / "c" / "distributed.exe"
RESULTS = ROOT / "results" / "distributed_memory.csv"

MPIEXEC = Path(
    r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
)

SAMPLE_INTERVAL = 0.005


def measure(n, processes):
    command = [
        str(MPIEXEC),
        "-n", str(processes),
        str(EXECUTABLE),
        str(n),
    ]

    start = time.perf_counter()
    launch_time = time.time()

    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    peak_memory = 0
    found_workers = False

    while process.poll() is None:
        total_memory = 0

        for worker in psutil.process_iter(
            ["name", "create_time", "memory_info"]
        ):
            try:
                if (
                    worker.info["name"]
                    and worker.info["name"].lower()
                    == EXECUTABLE.name.lower()
                    and worker.info["create_time"]
                    >= launch_time - 1
                ):
                    total_memory += worker.info[
                        "memory_info"
                    ].rss
                    found_workers = True

            except (psutil.NoSuchProcess,
                    psutil.AccessDenied):
                continue

        peak_memory = max(peak_memory, total_memory)
        time.sleep(SAMPLE_INTERVAL)

    output, _ = process.communicate()
    elapsed_ms = (time.perf_counter() - start) * 1000

    if process.returncode != 0 or "Validation: PASS" not in output:
        print(output)
        raise RuntimeError(
            f"MPI execution failed: n={n}, processes={processes}"
        )

    if not found_workers:
        raise RuntimeError(
            "No MPI worker processes were detected."
        )

    memory_mib = peak_memory / (1024 ** 2)

    return elapsed_ms, memory_mib


def main():
    if len(sys.argv) != 2:
        print("Usage: python measure_memory.py <size>")
        sys.exit(1)

    n = int(sys.argv[1])
    configurations = [1, 2, 4]

    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULTS, "a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow([
                "n",
                "processes",
                "end_to_end_ms",
                "peak_workers_rss_mib",
            ])

        for processes in configurations:
            elapsed, memory = measure(n, processes)

            writer.writerow([
                n,
                processes,
                f"{elapsed:.6f}",
                f"{memory:.6f}",
            ])

            print(
                f"n={n}, processes={processes}, "
                f"end-to-end={elapsed:.2f} ms, "
                f"peak workers RSS={memory:.2f} MiB"
            )


if __name__ == "__main__":
    main()
