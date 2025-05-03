from random import randint
from secp256k1 import *
import pickle
from hashlib import sha256

# cache of added Gs
cache = {}
with open("cache.pickle", "rb") as handle:
    cache = pickle.load(handle)

# generating private key
# private_key = randint(1, 999999999999999)
private_key = 308873889867894

# calculating public key
public_key = multiply(G, private_key, cache)

# getting message hash
message = "Hello web3"
h = sha256(message.encode("utf-8"))
h_int = int.from_bytes(h.digest(), byteorder="big")

# generating random nonce (k)
# k = randint(1, 99999999999999)  # nonce
k = 86349619429794

# signing message
R = multiply(G, k, cache)
r = R[0]
s = pow(k, -1, p) * (h_int + (r * private_key) % p) % p

# verification
R_prime = multiply(
    add(
        multiply(G, h_int, cache),
        multiply(public_key, r),
    ),
    pow(s, -1, p),
)

print(R_prime)
print(r)
print(R_prime[0])
