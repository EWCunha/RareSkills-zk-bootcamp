import galois
from functools import reduce
from py_ecc.bn128 import multiply


def interpolate_column_galois(col: galois.GF, points: galois.GF) -> galois.Poly:
    return galois.lagrange_poly(points, col)


def inner_product(a: any, b: any) -> any:
    mul_ = lambda x, y: x * y
    sum_ = lambda x, y: x + y
    return reduce(sum_, map(mul_, a, b))


def powers_of_tau(tau: int, degree: int, multiplier: int) -> list[int]:
    return [multiplier * tau**i for i in range(degree + 1)]


def calculate_values(
    multiplier: int, polys: list[galois.Poly], powers_of_tau: list
) -> list:
    print("\ncomeçou")
    print("multiplier", multiplier)
    result = []
    for poly in polys:
        inner_result = None
        print("degrees", poly.degrees[::-1])
        for i, coeff in enumerate(poly.coeffs[::-1]):
            if inner_result is None:
                inner_result = coeff * powers_of_tau[i]
            else:
                inner_result += coeff * powers_of_tau[i]

            print(type(powers_of_tau[i]))
            print("p_tau", i, powers_of_tau[i])
            print("coeff", i, coeff)
            print("inner_result", i, inner_result)

        print("mul", multiplier * inner_result)
        result.append(multiplier * inner_result)

    return result


def add_lists(list1: list, list2: list, list3: list) -> list:
    result = []
    for i in range(len(list1)):
        result.append(list1[i] + list2[i] + list3[i])

    return result


def generate_ec_points(generator: tuple, values: list) -> list[tuple]:
    result = []
    for value in values:
        result.append(multiply(generator, int(value)))

    return result
