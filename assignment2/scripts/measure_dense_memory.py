
import csv
import subprocess
import time
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parent.parent

sizes = [10, 50, 100, 200, 300, 500, 750, 1000]

commands = {
    "Baseline": ROOT / "c" / "baseline.exe",
    "Reordered": ROOT / "c" / "reordered.exe",
    "Blocked": ROOT / "c" / "blocked.exe"
}

output = ROOT / "results" / "dense_process_memory.csv"


with open(output, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["method", "size", "peak_rss_mib"])

    for method, executable in commands.items():
        for n in sizes:
            process = subprocess.Popen(
                [str(executable), "--memory", str(n)],
                cwd=ROOT,
                stdout=subprocess.DEVNULL
            )

            monitored = psutil.Process(process.pid)
            peak_memory = 0

            while True:
                try:
                    memory = monitored.memory_info().rss
                    peak_memory = max(peak_memory, memory)
                except psutil.NoSuchProcess:
                    pass

                if process.poll() is not None:
                    break

                time.sleep(0.001)

            if process.returncode != 0:
                raise RuntimeError(
                    f"{method} failed for size {n}"
                )

            peak_mib = peak_memory / (1024 * 1024)

            writer.writerow([method, n, peak_mib])

            print(f"{method} {n}x{n}: {peak_mib:.4f} MiB")
