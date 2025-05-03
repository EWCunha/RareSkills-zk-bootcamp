from py_ecc.bn128 import G1, curve_order, add, multiply

n = curve_order

A_val = 2
B_val = 5

val_1 = 2
val_2 = 20
val_3 = 3
val_4 = 4

mul_val1 = A_val * val_1 + B_val * val_2
mul_val2 = A_val * val_3 + B_val * val_4

A = multiply(G1, A_val)
B = multiply(G1, B_val)

res1 = add(multiply(A, val_1), multiply(B, val_2))
res1_eval = multiply(G1, mul_val1)
res2 = add(multiply(A, val_3), multiply(B, val_4))
res2_eval = multiply(G1, mul_val2)

print("A", A)
print("B", B)
print("mult1", mul_val1, res1 == res1_eval)
print("mult2", mul_val2, res2 == res2_eval)
