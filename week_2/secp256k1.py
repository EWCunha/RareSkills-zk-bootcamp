p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
h = 0x1
O = (0, 0)


def valid(P: tuple) -> bool:
    """
    Determine whether we have a valid representation of a point
    on our curve.  We assume that the x and y coordinates
    are always reduced modulo p, so that we can compare
    two points for equality with a simple ==.
    """

    x, y = P
    if P == O:
        return True
    else:
        return (y**2 - (x**3 + a * x + b)) % p == 0 and 0 <= x < p and 0 <= y < p


def inv_mod_p(x: int) -> int:
    """
    Compute an inverse for x modulo p, assuming that x
    is not divisible by p.
    """
    if x % p == 0:
        raise ZeroDivisionError("Impossible inverse")

    return pow(x, p - 2, p)


def inverse(P: tuple) -> int:
    """
    Inverse of the point P on the elliptic curve y^2 = x^3 + ax + b.
    """
    x, y = P
    if P == O:
        return P

    return x, (-y) % p


def add(P: tuple, Q: tuple) -> tuple:
    """
    Sum of the points P and Q on the elliptic curve y^2 = x^3 + ax + b.
    """
    if not (valid(P) and valid(Q)):
        raise ValueError("Invalid inputs")

    # Deal with the special cases where either P, Q, or P + Q is
    # the origin.
    x_p, y_p = P
    x_q, y_q = Q
    if P == O:
        result = Q
    elif Q == O:
        result = P
    elif Q == inverse(P):
        result = O
    else:
        # Cases not involving the origin.
        if P == Q:
            dydx = (3 * x_p**2 + a) * inv_mod_p(2 * y_p)
        else:
            dydx = (y_q - y_p) * inv_mod_p(x_q - x_p)

        x = (dydx**2 - x_p - x_q) % p
        y = (dydx * (x_p - x) - y_p) % p
        result = x, y

    return result


def multiply(P: tuple, num: int, cache: dict = {}) -> tuple:
    if cache == {}:
        i = [1, 2]
    else:
        i = sorted(list(cache.keys()))

    cache[1] = P
    while i[-1] <= num:
        cache[i[-1]] = add(cache[i[-2]], cache[i[-2]])
        i.append(i[-1] * 2)

    i = sorted(list(cache.keys()))
    index = -1
    point_mul = 0
    point = (0, 0)
    while point_mul < num:
        if i[index] > num:
            index -= 1
            continue
        elif point_mul + i[index] > num:
            index -= 1
            continue

        point = add(cache[i[index]], point)
        point_mul += i[index]
        index -= 1

    return point
