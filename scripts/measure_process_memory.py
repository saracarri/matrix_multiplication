
import csv
import subprocess
import sys
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parent.parent

sizes = [10, 50, 100, 200, 300]

commands = {
    "Python": [sys.executable, "python/matrix_multiplication.py"],
    "Java": ["java", "-cp", "java", "MatrixMultiplication"],
    "C": [str(ROOT / "c" / "matrix_multiplication.exe")]
}

output = ROOT / "results" / "process_memory_by_size.csv"

with open(output, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["language", "size", "peak_rss_mib"])

    for language, command in commands.items():
        for n in sizes:
            process = subprocess.Popen(
                command + [str(n)],
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
                    f"{language} failed for size {n}"
                )

            peak_mib = peak_memory / (1024 * 1024)

            writer.writerow([language, n, peak_mib])

            print(f"{language} {n}x{n}: {peak_mib:.4f} MiB")
