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
    FQ,
)
from random import randint

print(dir(G2))

A1 = (
    FQ(3932705576657793550893430333273221375907985235130430286685735064194643946083),
    FQ(18813763293032256545937756946359266117037834559191913266454084342712532869153),
)

print(neg(A1))
