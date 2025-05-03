from py_ecc.bn128 import G1, curve_order, add, multiply, b, field_modulus

n = curve_order

num_1 = 3
den_1 = 4
num_2 = 5
den_2 = 6

res_n = 19
res_d = 12

val_1 = num_1 * pow(den_1, -1, n) % n
val_2 = num_2 * pow(den_2, -1, n) % n

val_res = res_n * pow(res_d, -1, n) % n

A = multiply(G1, val_1)
B = multiply(G1, val_2)

print(val_res)
print("G", G1)
print("n", n)
print("A", A)
print("B", B)
print("result", add(A, B))


x = int(A[0])
y = int(A[1])


print(y**2 % field_modulus == (x**3 + int(b)) % field_modulus)
print(2**256 - 2**224 + 2**192 + 2**96 - 1, field_modulus)
print(int(0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF))
