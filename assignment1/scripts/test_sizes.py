
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))

from matrix_multiplication import load_matrix, matrix_multiplication

for n in [200, 300]:
    A = load_matrix(ROOT / "data" / f"A_{n}.csv")
    B = load_matrix(ROOT / "data" / f"B_{n}.csv")
    C = [[0] * n for _ in range(n)]

    start = time.perf_counter()
    matrix_multiplication(A, B, C)
    elapsed = time.perf_counter() - start

    print(f"Matrix size: {n}x{n}")
    print(f"Time: {elapsed:.4f} seconds")
    print()
