
import csv
import os
import subprocess
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SIZES = [100, 300, 500, 750, 1000]
THREAD_COUNTS = [1, 2, 4, 8, 16, 22]


def measure_memory(executable, n, threads=None):
    env = os.environ.copy()

    if threads is not None:
        env["OMP_NUM_THREADS"] = str(threads)

    process = subprocess.Popen(
        [str(executable), "--memory", str(n)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
    )

    monitored = psutil.Process(process.pid)
    peak_rss = 0

    while process.poll() is None:
        try:
            rss = monitored.memory_info().rss
            peak_rss = max(peak_rss, rss)
        except psutil.NoSuchProcess:
            break

        time.sleep(0.001)

    if process.wait() != 0:
        raise RuntimeError(f"Execution failed: {executable}, n={n}")

    return peak_rss / (1024 * 1024)


def main():
    RESULTS.mkdir(exist_ok=True)
    output = RESULTS / "process_memory.csv"

    with open(output, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["method", "size", "threads", "peak_rss_mib"])

        for n in SIZES:
            memory = measure_memory(ROOT / "c/sequential.exe", n)
            writer.writerow(["sequential", n, 1, f"{memory:.6f}"])
            print(f"Sequential | n={n} | RSS={memory:.3f} MiB")

        for threads in THREAD_COUNTS:
            for n in SIZES:
                memory = measure_memory(
                    ROOT / "c/parallel.exe", n, threads
                )

                writer.writerow(
                    ["parallel", n, threads, f"{memory:.6f}"]
                )

                print(
                    f"Parallel | threads={threads} | "
                    f"n={n} | RSS={memory:.3f} MiB"
                )

    print(f"\nMemory results saved to {output}")


if __name__ == "__main__":
    main()
