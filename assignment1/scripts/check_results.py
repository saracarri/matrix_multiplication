import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

for language in ["python", "java", "c"]:
    filename = RESULTS / f"{language}_times.csv"
    measurements = {}

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            n = int(row["size"])
            time_ms = float(row["time_seconds"]) * 1000
            measurements.setdefault(n, []).append(time_ms)

    print(f"\n{language.upper()}")

    for n in sorted(measurements):
        times = sorted(measurements[n])
        median = statistics.median(times)
        iqr = times[3] - times[1]

        print(f"{n}x{n}: Median = {median:.6f} ms, IQR = {iqr:.6f} ms")
