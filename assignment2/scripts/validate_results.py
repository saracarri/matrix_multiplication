
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_matrix(filename):
    with open(filename, newline="") as file:
        return [
            [int(value) for value in row]
            for row in csv.reader(file)
        ]


def reference_multiplication(A, B):
    n = len(A)

    return [
        [sum(A[i][k] * B[k][j] for k in range(n))
         for j in range(n)]
        for i in range(n)
    ]


def save_matrix(matrix, filename):
    with open(filename, "w", newline="") as file:
        csv.writer(file).writerows(matrix)


if __name__ == "__main__":
    output_dir = ROOT / "data" / "expected"
    output_dir.mkdir(exist_ok=True)

    for n in [500, 750, 1000]:
        A = load_matrix(ROOT / "data" / f"A_{n}.csv")
        B = load_matrix(ROOT / "data" / f"B_{n}.csv")

        expected = reference_multiplication(A, B)

        save_matrix(expected, output_dir / f"C_{n}.csv")

        print(f"Reference result generated for {n}x{n}")
