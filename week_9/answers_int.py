import numpy as np
import galois
from py_ecc.bn128 import curve_order
from aux_functions import *
import random


L = np.array(
    [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
    ]
)

R = np.array(
    [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
    ]
)

O = np.array(
    [
        [curve_order - 2, 3, 0, 0, 0],
        [curve_order - 2, 0, 3, 0, 0],
        [curve_order - 2, 0, 0, 3, 0],
        [curve_order - 2, 0, 0, 0, 3],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
    ]
)

x1 = 1
x2 = 2
x3 = 1
x4 = 2
a = np.array([1, x1, x2, x3, x4])

# assert all(
#     np.equal(np.matmul(L, a) * np.matmul(R, a), np.matmul(O, a))
# ), "matrices not equal"

GF = galois.GF(curve_order)

L_galois = GF(L)
R_galois = GF(R)
O_galois = GF(O)

a_galois = GF(a)

assert all(
    np.equal(
        np.matmul(L_galois, a_galois) * np.matmul(R_galois, a_galois),
        np.matmul(O_galois, a_galois),
    )
), "Galois matrices not equal"

points = GF(np.array(range(1, L_galois.shape[0] + 1)))
U_polys_galois = np.apply_along_axis(interpolate_column_galois, 0, L_galois, points)
V_polys_galois = np.apply_along_axis(interpolate_column_galois, 0, R_galois, points)
W_polys_galois = np.apply_along_axis(interpolate_column_galois, 0, O_galois, points)


sum_au: galois.Poly = inner_product(U_polys_galois, a_galois)
sum_bu: galois.Poly = inner_product(V_polys_galois, a_galois)
sum_cu: galois.Poly = inner_product(W_polys_galois, a_galois)

# Defining t(x)
t = None
for i in range(sum_au.degree + 1):
    if t is None:
        t = galois.Poly([1, curve_order - (i + 1)], field=GF)
        continue

    t *= galois.Poly([1, curve_order - (i + 1)], field=GF)


h: galois.Poly = (sum_au * sum_bu - sum_cu) // t

assert sum_au * sum_bu == sum_cu + h * t, "division has a remainder"


tau = GF(random.randint(1, 10) % curve_order)
ht: galois.Poly = h * t

p_tau_a = powers_of_tau(tau, sum_au.degree, 1)
p_tau_b = powers_of_tau(tau, sum_bu.degree, 1)
p_tau_c = powers_of_tau(tau, sum_cu.degree, 1)
p_tau_ht = powers_of_tau(tau, t.degree - 1, t(tau))


alpha = GF(random.randint(1, 10000) % curve_order)
beta = GF(random.randint(1, 10000) % curve_order)

A_inner = inner_product(p_tau_a, sum_au.coeffs[::-1])
A = alpha + A_inner


B_inner = inner_product(p_tau_b, sum_bu.coeffs[::-1])
B = beta + B_inner

C = inner_product(p_tau_c, sum_cu.coeffs[::-1])
ht_prime = inner_product(p_tau_ht, ht.coeffs[::-1])
alpha_v = alpha * B_inner
beta_u = beta * A_inner

alpha_beta = alpha * beta

assert A * B == alpha_beta + C + ht_prime + alpha_v + beta_u, "invalid proof"
