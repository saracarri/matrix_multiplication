
import csv
import random
from pathlib import Path

def generate_matrix(n, seed):
    rng = random.Random(seed)
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            row.append(rng.randint(0, 9))
        matrix.append(row)

    return matrix


def save_matrix(matrix, filename):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(matrix)


if __name__ == "__main__":
    sizes = [10, 50, 100]
    data_dir = Path(__file__).resolve().parent.parent / "data"

    data_dir.mkdir(exist_ok=True)

    for n in sizes:
        A = generate_matrix(n, 42)
        B = generate_matrix(n, 43)

        save_matrix(A, data_dir / f"A_{n}.csv")
        save_matrix(B, data_dir / f"B_{n}.csv")

        print(f"Generated matrices of size {n}x{n}")
