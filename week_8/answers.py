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
from functools import reduce

# print(multiply(G1, -2))

## R1CS to QAP
# Define the matrices
A = np.array([[0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 1, 0, 0, 0]])

B = np.array([[0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 5, 0, 0]])

C = np.array([[0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [-3, 1, 1, 2, 0, -1]])

# pick random values for x and y
x = random.randint(1, 10)
y = random.randint(1, 10)

# this is our orignal formula
out = (
    3 * x * x * y + 5 * x * y - x - 2 * y + 3
)  # the witness vector with the intermediate variables inside
v1 = 3 * x * x
v2 = v1 * y
w = np.array([1, out, x, y, v1, v2])

result = C.dot(w) == np.multiply(A.dot(w), B.dot(w))
assert result.all(), "result contains an inequality"


def convert_to_polynomial(matrix: np.ndarray) -> np.ndarray:
    pol_matrix = np.zeros(matrix.shape)
    x_vals = np.array([i + 1 for i in range(matrix.shape[0])])
    for i_col, col in enumerate(matrix.T):
        pol_matrix[:, i_col] = lagrange(x_vals, col)

    return pol_matrix


# Converting matrix columns into polynomials
A_pol = convert_to_polynomial(A)
B_pol = convert_to_polynomial(B)
C_pol = convert_to_polynomial(C)

# Calculate sums
A_sum = np.matmul(A_pol, w)
B_sum = np.matmul(B_pol, w)
C_sum = np.matmul(C_pol, w)

a = np.poly1d(A_sum)
b = np.poly1d(B_sum)
c = np.poly1d(C_sum)

# Defining t(x)
t_x = 1
for i in range(a.order):
    t_x *= np.poly1d([1, -(i + 1)])

# Calculating h(x)
h_x = (a * b - c) / t_x

assert a * b == c + t_x * h_x[0]

# print("a:\n", a)
# print("b:\n", b)
# print("c:\n", c)
# print("t:\n", t_x)
# print("h:\n", h_x[0])
assert h_x[1] == np.poly1d([0])


def generate_powers_of_tau(
    tau: int, degree: int, generator: tuple, multiplier: int
) -> list:
    return [multiply(generator, int(multiplier * tau**i)) for i in range(degree + 1)]


def inner_product(powers_of_tau: list, coeffs: list) -> tuple:
    result = None
    for i in range(len(powers_of_tau)):
        if coeffs[i] < 0:
            coef = curve_order + coeffs[i]
        else:
            coef = coeffs[i]
        result = add(multiply(powers_of_tau[i], coef), result)

    return result


def sum_power(
    powers_of_tau: list, coeffs_matrix: np.ndarray, witness: np.ndarray
) -> tuple:
    result = None
    for i in range(len(witness)):
        if np.any(coeffs_matrix[:, i]):
            result = add(
                multiply(
                    inner_product(powers_of_tau, coeffs_matrix[:, i][::-1]), witness[i]
                ),
                result,
            )

    return result


tau = random.randint(1, 10)

powers_of_tau_G1 = generate_powers_of_tau(tau, a.order, G1, 1)
powers_of_tau_G2 = generate_powers_of_tau(tau, a.order, G2, 1)
powers_of_tau_tG1 = generate_powers_of_tau(tau, a.order, G1, t_x(tau))

A1 = sum_power(powers_of_tau_G1, A_pol, w)
B2 = sum_power(powers_of_tau_G2, B_pol, w)
C_prime1 = sum_power(powers_of_tau_G1, C_pol, w)
HT1 = inner_product(powers_of_tau_tG1, h_x[0].coeffs[::-1])
C1 = add(C_prime1, HT1)


identity = FQ12(
    [
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
)

g12_sum = final_exponentiate(pairing(B2, A1) * pairing(G2, neg(C1)))

print(eq(identity, g12_sum))
print(A1)
print(B2)
print(C1)
