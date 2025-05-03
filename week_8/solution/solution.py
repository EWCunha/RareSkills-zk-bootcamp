import numpy as np
import galois
from functools import reduce
from py_ecc.bn128 import G1, G2, multiply, add, curve_order, eq, Z1, pairing

GF = galois.GF(curve_order)

# R1CS

# 1, out, x, y, v1, v2, v3
L = np.array(
    [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, curve_order - 5, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ]
)

R = np.array(
    [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
    ]
)

O = np.array(
    [
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, curve_order - 1, 0],
    ]
)

L_galois = GF(L)
R_galois = GF(R)
O_galois = GF(O)

# Witness

x = GF(4)
y = GF(curve_order - 2)
v1 = x * x
v2 = v1 * v1  # x^4
v3 = GF(curve_order - 5) * y * y
out = v3 * v1 + v2  # -5y^2 * x^2

witness = GF(np.array([1, out, x, y, v1, v2, v3]))

assert all(
    np.equal(
        np.matmul(L_galois, witness) * np.matmul(R_galois, witness),
        np.matmul(O_galois, witness),
    )
), "not equal"

# Lagrange interpolation


def interpolate_column(col):
    xs = GF(np.array([1, 2, 3, 4]))
    return galois.lagrange_poly(xs, col)


# axis 0 is the columns. apply_along_axis is the same as doing a for loop over the columns and collecting the results in an array
U_polys = np.apply_along_axis(interpolate_column, 0, L_galois)
V_polys = np.apply_along_axis(interpolate_column, 0, R_galois)
W_polys = np.apply_along_axis(interpolate_column, 0, O_galois)

# QAP


def inner_product_polynomials_with_witness(polys, witness):
    mul_ = lambda x, y: x * y
    sum_ = lambda x, y: x + y
    return reduce(sum_, map(mul_, polys, witness))


# U * a
term_1 = inner_product_polynomials_with_witness(U_polys, witness)
# V * a
term_2 = inner_product_polynomials_with_witness(V_polys, witness)
# W * a
term_3 = inner_product_polynomials_with_witness(W_polys, witness)

# t = (x - 1)(x - 2)(x - 3)(x - 4)
t = (
    galois.Poly([1, curve_order - 1], field=GF)
    * galois.Poly([1, curve_order - 2], field=GF)
    * galois.Poly([1, curve_order - 3], field=GF)
    * galois.Poly([1, curve_order - 4], field=GF)
)

h = (term_1 * term_2 - term_3) // t

HT = h * t

assert term_1 * term_2 == term_3 + HT, "division has a remainder"

print(f"U_polys: {U_polys}")
print(f"V_polys: {V_polys}")
print(f"W_polys: {W_polys}")
print(f"HT: {HT}")

# Encrypted polynomial evaluation


def inner_product(ec_points, coeffs):
    return reduce(
        add,
        (multiply(point, int(coeff)) for point, coeff in zip(ec_points, coeffs)),
        Z1,
    )


def generate_powers_of_tau_G1(tau, degree):
    return [multiply(G1, int(tau**i)) for i in range(degree + 1)]


def generate_powers_of_tau_G2(tau, degree):
    return [multiply(G2, int(tau**i)) for i in range(degree + 1)]


# evaluate at 8
tau = GF(8)


def encrypted_evaluation_G1(p):
    powers_of_tau = generate_powers_of_tau_G1(tau, p.degree)
    evaluate_on_ec = inner_product(powers_of_tau, p.coeffs[::-1])

    return evaluate_on_ec


def encrypted_evaluation_G2(p):
    powers_of_tau = generate_powers_of_tau_G2(tau, p.degree)
    evaluate_on_ec = inner_product(powers_of_tau, p.coeffs[::-1])

    return evaluate_on_ec


U_evaluated_on_ec = encrypted_evaluation_G1(term_1)
V_evaluated_on_ec = encrypted_evaluation_G2(term_2)
W_evaluated_on_ec = encrypted_evaluation_G1(term_3)
HT_evaluated_on_ec = encrypted_evaluation_G1(HT)

print(f"U_evaluated_on_ec : {U_evaluated_on_ec}")
print(f"V_evaluated_on_ec: {V_evaluated_on_ec}")
print(f"W_evaluated_on_ec: {W_evaluated_on_ec}")
print(f"HT_evaluated_on_ec: {HT_evaluated_on_ec}")

A1 = U_evaluated_on_ec
B2 = V_evaluated_on_ec
C1 = add(W_evaluated_on_ec, HT_evaluated_on_ec)

print(f"A1: {A1}")
print(f"B2: {B2}")
print(f"C1: {C1}")

print(f"pairing(B2, A1): {pairing(B2, A1)}")
print(f"pairing(G2, C1): {pairing(G2, C1)}")

assert eq(pairing(B2, A1), pairing(G2, C1))
