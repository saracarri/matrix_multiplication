
import csv
import random
from pathlib import Path


def generate_sparse_matrix(n, sparsity, seed):
    rng = random.Random(seed)

    total = n * n
    nnz = round(total * (1 - sparsity))

    matrix = [[0] * n for _ in range(n)]

    # Select positions for nonzero elements
    positions = rng.sample(range(total), nnz)

    for pos in positions:
        i = pos // n
        j = pos % n
        matrix[i][j] = rng.randint(1, 9)

    return matrix


def save_matrix(matrix, filename):
    with open(filename, "w", newline="") as file:
        csv.writer(file).writerows(matrix)


if __name__ == "__main__":
    sizes = [100, 300, 500, 750, 1000]
    sparsities = [0.50, 0.90, 0.95, 0.99]

    data_dir = Path(__file__).resolve().parent.parent / "data" / "sparse"
    data_dir.mkdir(parents=True, exist_ok=True)

    for n in sizes:
        for sparsity in sparsities:
            percentage = int(sparsity * 100)

            A = generate_sparse_matrix(n, sparsity, 42)
            B = generate_sparse_matrix(n, sparsity, 43)

            save_matrix(A, data_dir / f"A_{n}_{percentage}.csv")
            save_matrix(B, data_dir / f"B_{n}_{percentage}.csv")

            print(f"Generated {n}x{n} matrices with {percentage}% zeros")
