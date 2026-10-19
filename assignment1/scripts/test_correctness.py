import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python"))

from matrix_multiplication import matrix_multiplication

failures = 0


def check(name, actual, expected):
    global failures

    if actual == expected:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}")
        failures += 1


def multiply(A, B):
    n = len(A)
    C = [[7] * n for _ in range(n)]  # non-zero values to check the reset
    return matrix_multiplication(A, B, C)


# 2x2 case with a result calculated by hand
check("2x2 known result",
      multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
      [[19, 22], [43, 50]])

n = 4
M = [[i * n + j + 1 for j in range(n)] for i in range(n)]
I = [[int(i == j) for j in range(n)] for i in range(n)]
Z = [[0] * n for _ in range(n)]

check("A x I = A", multiply(M, I), M)
check("I x A = A", multiply(I, M), M)
check("A x 0 = 0", multiply(M, Z), Z)
check("0 x A = 0", multiply(Z, M), Z)

if failures:
    print(f"{failures} test(s) failed")
    sys.exit(1)

print("All Python correctness tests passed")
