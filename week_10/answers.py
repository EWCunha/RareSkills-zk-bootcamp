import numpy as np
import galois
from aux_functions import *
import random
from py_ecc.bn128 import (
    G1,
    G2,
    multiply,
    curve_order,
    eq,
    pairing,
    final_exponentiate,
    neg,
    FQ12,
    add,
)


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
        [-2, 3, 0, 0, 0],
        [-2, 0, 3, 0, 0],
        [-2, 0, 0, 3, 0],
        [-2, 0, 0, 0, 3],
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

assert all(
    np.equal(np.matmul(L, a) * np.matmul(R, a), np.matmul(O, a))
), "matrices not equal"

# curve_order = 79
GF = galois.GF(curve_order)

L_galois = GF(L % curve_order)
R_galois = GF(R % curve_order)
O_galois = GF(O % curve_order)

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


# tau = GF(random.randint(1, 10) % curve_order)
tau = GF(3)
ht: galois.Poly = h * t

p_tau_a = powers_of_tau(tau, sum_au.degree, 1)
p_tau_b = powers_of_tau(tau, sum_bu.degree, 1)
p_tau_c = powers_of_tau(tau, sum_cu.degree, 1)
p_tau_ht = powers_of_tau(tau, t.degree - 1, t(tau))


# alpha = GF(random.randint(1, 10000) % curve_order)
# beta = GF(random.randint(1, 10000) % curve_order)
# gamma = GF(random.randint(1, 10000) % curve_order)
# delta = GF(random.randint(1, 10000) % curve_order)
# r = GF(random.randint(1, 10000) % curve_order)
# s = GF(random.randint(1, 10000) % curve_order)
# l = random.randint(1, len(a) - 1)
alpha = GF(54)
beta = GF(67)
gamma = GF(13)
delta = GF(7)
r = GF(17)
s = GF(25)
l = 3

a_coeffs = sum_au.coeffs[::-1]
b_coeffs = sum_bu.coeffs[::-1]
c_coeffs = sum_cu.coeffs[::-1]
ht_coeffs = ht.coeffs[::-1]

A_inner = inner_product(p_tau_a, a_coeffs)
A = alpha + A_inner + r * delta


B_inner = inner_product(p_tau_b, b_coeffs)
B = beta + B_inner + s * delta

C_pub = inner_product(p_tau_c[:l], c_coeffs[:l])
alpha_v_pub = alpha * inner_product(p_tau_b[:l], b_coeffs[:l])
beta_u_pub = beta * inner_product(p_tau_a[:l], a_coeffs[:l])

C_priv = inner_product(p_tau_c[l:], c_coeffs[l:])
alpha_v_priv = alpha * inner_product(p_tau_b[l:], b_coeffs[l:])
beta_u_priv = beta * inner_product(p_tau_a[l:], a_coeffs[l:])
ht_prime = inner_product(p_tau_ht, ht_coeffs)

term_pub = (C_pub + alpha_v_pub + beta_u_pub) / gamma
term_priv = (
    (C_priv + alpha_v_priv + beta_u_priv + ht_prime) / delta
    + s * A
    + r * B
    - r * s * delta
)


assert A * B == alpha * beta + term_pub * gamma + term_priv * delta, "invalid proof"

alpha_1 = multiply(G1, int(alpha))
beta_1 = multiply(G1, int(beta))
delta_1 = multiply(G1, int(delta))

beta_2 = multiply(G2, int(beta))
delta_2 = multiply(G2, int(delta))
gamma_2 = multiply(G2, int(gamma))


A = alpha + A_inner
shift_A1 = multiply(delta_1, int(r))
A1 = add(multiply(G1, int(A)), shift_A1)

B = beta + B_inner
shift_B1 = multiply(delta_1, int(s))
shift_B2 = multiply(delta_2, int(s))
B2 = add(multiply(G2, int(B)), shift_B2)
B1 = add(multiply(G1, int(B)), shift_B1)

term_pub_1 = multiply(G1, int(term_pub))

C1_termA = multiply(A1, int(s))
C1_termB = multiply(B1, int(r))
C1_term_rs = neg(multiply(delta_1, int(r * s)))
C1_term = multiply(G1, int((C_priv + alpha_v_priv + beta_u_priv + ht_prime) / delta))
C1_add1 = add(C1_termA, C1_termB)
C1_add2 = add(C1_term, C1_term_rs)
C1 = add(C1_add1, C1_add2)


alpha_beta_pair = pairing(beta_2, alpha_1)
C1_delta_2_pair = pairing(delta_2, C1)
term_pub_1_gamm_2_pair = pairing(gamma_2, term_pub_1)

# A1_B2_pair = pairing(B2, A1)
# assert eq(left_side, right_side), "invalid proof"

negA1_B2_pair = pairing(B2, neg(A1))
assert eq(
    final_exponentiate(
        alpha_beta_pair * term_pub_1_gamm_2_pair * C1_delta_2_pair * negA1_B2_pair
    ),
    FQ12.one(),
)

# For the verifying contract

print("U_polys_galois", U_polys_galois)
print()

vals1 = calculate_values(beta / gamma, U_polys_galois[:l], p_tau_a)
vals2 = calculate_values(alpha / gamma, V_polys_galois[:l], p_tau_b)
vals3 = calculate_values(GF(1) / gamma, W_polys_galois[:l], p_tau_c)

print("vals1", vals1)
print()

vals = add_lists(vals1, vals2, vals3)

print("vals", vals)
print()

ec_points_pub = generate_ec_points(G1, vals)

print("ec_points_pub", ec_points_pub)
print()
print("alpha_1", alpha_1)
print()
print("beta_2", beta_2)
print()
print("delta_2", delta_2)
print()
print("gamma_2", gamma_2)
print()
print("l", l)
print()
print("a_galois", a_galois[:l])
print()
print("A1", A1)
print()
print("B2", B2)
print()
print("C1", C1)

addedPubPoints = None
for input, point in zip(a_galois[:l], ec_points_pub):
    addedPubPoints = add(addedPubPoints, multiply(point, int(input)))

pub_times_input_pair = pairing(gamma_2, addedPubPoints)

print(term_pub_1_gamm_2_pair)
print(pub_times_input_pair)


assert eq(
    final_exponentiate(
        alpha_beta_pair * pub_times_input_pair * C1_delta_2_pair * negA1_B2_pair
    ),
    FQ12.one(),
)
