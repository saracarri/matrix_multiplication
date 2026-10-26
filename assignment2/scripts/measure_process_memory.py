
import csv
import subprocess
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parent.parent

sizes = [100, 300, 500, 750, 1000]
sparsities = [50, 90, 95, 99]

command = [str(ROOT / "c" / "sparse_csr.exe")]
output = ROOT / "results" / "sparse_process_memory.csv"

with open(output, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["size", "sparsity", "peak_rss_mib"])

    for n in sizes:
        for sparsity in sparsities:
            process = subprocess.Popen(
                command + ["--memory", str(n), str(sparsity)],
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
                    f"CSR failed for size {n}, sparsity {sparsity}"
                )

            peak_mib = peak_memory / (1024 * 1024)

            writer.writerow([n, sparsity, peak_mib])

            print(
                f"{n}x{n}, {sparsity}% zeros: "
                f"{peak_mib:.4f} MiB"
            )
