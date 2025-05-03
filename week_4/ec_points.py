from py_ecc.bn128 import (
    G1,
    G2,
    curve_order,
    add,
    multiply,
    pairing,
    final_exponentiate,
    eq,
    neg,
    FQ12,
)
from random import randint


def find_integer_divisor(start: int, number: int) -> tuple[int, int]:
    while number % start != 0:
        start += 1
        if start > number:
            raise ValueError("No integer divisor found")

    return int(start), int(number / start)


max_int = 5

alfa_1 = randint(2, max_int)
beta_2 = randint(2, max_int)
gamma_2 = randint(2, max_int)
delta_2 = randint(2, max_int)

a = randint(2, max_int)
x1 = randint(2, max_int)
x2 = randint(2, max_int)
x3 = randint(2, max_int)
c = randint(2, max_int)

a, b = find_integer_divisor(a, alfa_1 * beta_2 + (x1 + x2 + x3) * gamma_2 + c * delta_2)

assert -a * b + alfa_1 * beta_2 + (x1 + x2 + x3) * gamma_2 + c * delta_2 == 0

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


Alfa_1 = multiply(G1, alfa_1)
Beta_2 = multiply(G2, beta_2)
Gamma_2 = multiply(G2, gamma_2)
Delta_2 = multiply(G2, delta_2)

A1 = multiply(G1, a)
B2 = multiply(G2, b)
X1 = multiply(G1, x1 + x2 + x3)
C1 = multiply(G1, c)

assert eq(
    identity,
    final_exponentiate(
        pairing(B2, neg(A1))
        * pairing(Beta_2, Alfa_1)
        * pairing(Gamma_2, X1)
        * pairing(Delta_2, C1)
    ),
)

print("Alfa_1:", Alfa_1)
print("Beta_2:", Beta_2)
print("Gamma_2:", Gamma_2)
print("Delta_2:", Delta_2)
print("A1:", A1)
print("B2:", B2)
print("X1:", X1)
print("C1:", C1)
print("x1:", x1)
print("x2:", x2)
print("x3:", x3)

# print(type(A1))
print(neg(A1))

print(curve_order)
