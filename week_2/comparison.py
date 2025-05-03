from ecpy.curves import Curve
from eth_utils import keccak

# private_key = 0xAC0974BEC39A17E36BA4A6B4D238FF944BACB478CBED5EFCAE784D7BF4F2FF80
private_key = 308873889867894

cv = Curve.get_curve("secp256k1")
print(type(cv.generator))
print(cv.generator)
print(private_key * cv.generator)
pu_key = (
    private_key * cv.generator
)  # just multiplying the private key by generator point (EC multiplication)

concat_x_y = pu_key.x.to_bytes(32, byteorder="big") + pu_key.y.to_bytes(
    32, byteorder="big"
)
eth_addr = "0x" + keccak(primitive=concat_x_y)[-20:].hex()

print("private key: ", hex(private_key))
print("eth_address: ", eth_addr)
