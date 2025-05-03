import galois
from functools import reduce


def interpolate_column_galois(col: galois.GF, points: galois.GF) -> galois.Poly:
    return galois.lagrange_poly(points, col)


def inner_product(a: any, b: any) -> any:
    mul_ = lambda x, y: x * y
    sum_ = lambda x, y: x + y
    return reduce(sum_, map(mul_, a, b))


def powers_of_tau(tau: int, degree: int, multiplier: int) -> list[int]:
    return [multiplier * tau**i for i in range(degree + 1)]
