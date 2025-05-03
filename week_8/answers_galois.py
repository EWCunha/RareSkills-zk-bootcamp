import numpy as np
import random
from scipy.interpolate import lagrange
from py_ecc.bn128 import (
    G1,
    G2,
    multiply,
    add,
    curve_order,
    eq,
    Z1,
    FQ,
    pairing,
    final_exponentiate,
    neg,
    FQ12,
    field_modulus,
)
import galois
from functools import reduce
import pickle


## R1CS to QAP
# Define the matrices
A = np.array([[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]])

B = np.array([[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]])

C = np.array(
    [
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1],
        [-3, 1, 1, 2, 0, -1],
    ]
)

# pick random values for x and y
x = random.randint(1, 10)
y = random.randint(1, 10)

# this is our orignal formula
v1 = 3 * x * x
v2 = v1 * y
out = (
    v2 + 5 * x * y - x - 2 * y + 3
)  # the witness vector with the intermediate variables inside
w = np.array([1, out, x, y, v1, v2])

result = C.dot(w) == np.multiply(A.dot(w), B.dot(w))
assert result.all(), "result contains an inequality"

## Galois


# curve_order = 79
GF = galois.GF(curve_order)

A_galois = GF((A + curve_order) % curve_order)
B_galois = GF((B + curve_order) % curve_order)
C_galois = GF((C + curve_order) % curve_order)
w_galois = GF((w + curve_order) % curve_order)

assert all(
    np.equal(
        np.matmul(A_galois, w_galois) * np.matmul(B_galois, w_galois),
        np.matmul(C_galois, w_galois),
    )
), "not equal"


def interpolate_points(coeffs_matrix: np.ndarray) -> np.ndarray:
    xs = GF(np.array(range(1, coeffs_matrix.shape[0] + 1)))
    result = []
    for col in coeffs_matrix.T:
        result.append(galois.lagrange_poly(xs, col))

    return np.array(result)


def interpolate_column_galois(col):
    xs = GF(np.array(range(1, len(col) + 1)))
    return galois.lagrange_poly(xs, col)


def inner_product(a: np.ndarray, b: galois.GF) -> galois.Poly:
    mul_ = lambda x, y: x * y
    sum_ = lambda x, y: x + y
    return reduce(sum_, map(mul_, a, b))


# Converting matrix columns into polynomials
A_pol = interpolate_points(A_galois)
B_pol = interpolate_points(B_galois)
C_pol = interpolate_points(C_galois)

# Calculate sums
A_sum = inner_product(A_pol, w_galois)
B_sum = inner_product(B_pol, w_galois)
C_sum = inner_product(C_pol, w_galois)


# Defining t(x)
t_x = None
for i in range(A_sum.degree):
    if t_x is None:
        t_x = galois.Poly([1, curve_order - (i + 1)], field=GF)
        continue

    t_x *= galois.Poly([1, curve_order - (i + 1)], field=GF)


# Calculating h(x)
h_x = (A_sum * B_sum - C_sum) // t_x

assert A_sum * B_sum == C_sum + t_x * h_x


def generate_powers_of_tau(tau: int, degree: int, multiplier: int) -> list:
    return [int(multiplier * tau**i) for i in range(degree + 1)]


def powers_of_tau_product(powers_of_tau: list, coeffs: list) -> int:
    result = None
    for i in range(len(powers_of_tau)):
        if result is None:
            result = powers_of_tau[i] * coeffs[i]
            continue

        result += powers_of_tau[i] * coeffs[i]

    return result


tau = random.randint(1, 10)

ht = t_x * h_x

powers_of_tau_A1 = generate_powers_of_tau(tau, A_sum.degree, 1)
powers_of_tau_B2 = generate_powers_of_tau(tau, B_sum.degree, 1)
powers_of_tau_C_prime1 = generate_powers_of_tau(tau, C_sum.degree, 1)
powers_of_tau_HT1 = generate_powers_of_tau(tau, ht.degree, 1)

A1 = powers_of_tau_product(powers_of_tau_A1, A_sum.coeffs[::-1])
B2 = powers_of_tau_product(powers_of_tau_B2, B_sum.coeffs[::-1])
C_prime1 = powers_of_tau_product(powers_of_tau_C_prime1, C_sum.coeffs[::-1])
HT1 = powers_of_tau_product(powers_of_tau_HT1, ht.coeffs[::-1])
C1 = C_prime1 + HT1

assert A1 * B2 == C1


A1_G1 = multiply(G1, int(A1))
B2_G2 = multiply(G2, int(B2))
C1_G1 = multiply(G1, int(C1))

assert eq(pairing(B2_G2, A1_G1), pairing(G2, C1_G1))
