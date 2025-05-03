from random import randint
from ecpy.curves import Curve
from eth_utils import keccak

# secp256k1 curve
cv = Curve.get_curve("secp256k1")
G = cv.generator
n = cv.order

# generating private key
private_key = randint(1, 999999999999999)

# calculating public key
public_key = private_key * G

# getting message hash
message = "Hello web3"
h = keccak(text=message)
h_int = int.from_bytes(h, byteorder="big")

# generating random nonce (k)
k = randint(1, 99999999999999)  # nonce

# signing message
R = k * G
r = R.x
s = pow(k, -1, n) * ((h_int + (r * private_key) % n) % n) % n

# verification
R_prime = pow(s, -1, n) * (h_int * G + r * public_key)

print(r, s)
print(R_prime.x == r)
