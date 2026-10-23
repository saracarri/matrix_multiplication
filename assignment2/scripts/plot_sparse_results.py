
import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


with open(RESULTS / "sparse_times.csv", newline="") as file:
    times = list(csv.DictReader(file))

with open(RESULTS / "sparse_memory.csv", newline="") as file:
    memories = list(csv.DictReader(file))


sizes = sorted({int(row["size"]) for row in times})
sparsities = sorted({int(row["sparsity"]) for row in times})


def median_ms(size, sparsity, field):
    values = []

    for row in times:
        if int(row["size"]) == size and int(row["sparsity"]) == sparsity:
            values.append(float(row[field]) * 1000)

    if len(values) != 5:
        raise ValueError("Expected five measurements per configuration")

    return median(values)


# Compare dense and CSR multiplication for each sparsity level
for sparsity in sparsities:
    dense = []
    csr = []

    for n in sizes:
        dense.append(median_ms(n, sparsity, "dense_time_seconds"))
        csr.append(median_ms(n, sparsity, "csr_time_seconds"))

    plt.figure(figsize=(7, 4.5))

    plt.plot(sizes, dense, marker="o", label="Dense (i-k-j)")
    plt.plot(sizes, csr, marker="s", label="CSR multiplication")

    plt.xlabel("Matrix size (n x n)")
    plt.ylabel("Median multiplication time (ms)")
    plt.title(f"Dense vs CSR - {sparsity}% zeros")

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIGURES / f"sparse_time_{sparsity}.png", dpi=180)
    plt.close()


# Calculate CSR speedup without conversion time
plt.figure(figsize=(7, 4.5))

for sparsity in sparsities:
    speedups = []

    for n in sizes:
        dense_time = median_ms(n, sparsity, "dense_time_seconds")
        csr_time = median_ms(n, sparsity, "csr_time_seconds")

        speedups.append(dense_time / csr_time)

    plt.plot(sizes, speedups, marker="o", label=f"{sparsity}% zeros")

plt.xlabel("Matrix size (n x n)")
plt.ylabel("Speedup (Dense / CSR)")
plt.title("CSR multiplication speedup (conversion excluded)")

plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "sparse_speedup.png", dpi=180)
plt.close()


# Compare estimated storage for the largest matrix size
largest = max(sizes)

rows = []

for row in memories:
    if int(row["size"]) == largest:
        rows.append(row)

rows.sort(key=lambda row: int(row["sparsity"]))

if len(rows) != len(sparsities):
    raise ValueError("Missing storage configurations")


zero_percentages = []
dense_storage = []
csr_storage = []

for row in rows:
    zero_percentages.append(int(row["sparsity"]))
    dense_storage.append(float(row["dense_storage_mib"]))
    csr_storage.append(float(row["csr_storage_mib"]))


plt.figure(figsize=(7, 4.5))

plt.plot(zero_percentages, dense_storage,
         marker="o", label="Dense A+B+C")

plt.plot(zero_percentages, csr_storage,
         marker="s", label="CSR A+B + dense C")

plt.xlabel("Zero entries (%)")
plt.ylabel("Estimated array storage (MiB)")
plt.title(f"Estimated representation storage - {largest} x {largest}")

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(FIGURES / "sparse_memory_1000.png", dpi=180)
plt.close()


print(f"Saved {len(sparsities) + 2} plots to {FIGURES}")
