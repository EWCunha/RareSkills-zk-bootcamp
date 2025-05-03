import numpy as np
import random
from py_ecc.bn128 import curve_order
import galois
import pickle

GF = galois.GF(curve_order)

## R1CS to QAP
# 1, out, x, y, v1, v2, v3
A = GF(
    np.array(
        [
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, (-5) % curve_order, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ]
    )
)

B = GF(
    np.array(
        [
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
        ]
    )
)

C = GF(
    np.array(
        [
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, (-1) % curve_order, 0],
        ]
    )
)

# pick random values for x and y
x = GF(random.randint(1, 10))
y = GF(random.randint(1, 10))

# this is our orignal formula

v1 = x * x
v2 = v1 * v1
v3 = GF((-5) % curve_order) * y * y
out = v3 * v1 + v2
w = GF(np.array([1, out, x, y, v1, v2, v3]))

assert all(np.equal(np.matmul(A, w) * np.matmul(B, w), np.matmul(C, w))), "not equal"

with open("qap.pickle", "wb") as f:
    pickle.dump((A, B, C, w, GF), f, fix_imports=True)
