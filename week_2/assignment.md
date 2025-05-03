Implement ECDSA from scratch. You want to use the secp256k1 curve. See here for a reference library: https://www.rareskills.io/post/generate-ethereum-address-from-private-key-python

1) pick a private key

2) generate the public key using that private key (not the eth address, the public key)

3) pick message m and hash it to produce h (h can be though of as a 256 bit number)

4) sign m using your private key and a randomly chosen nonce k. produce (r, s, h, PubKey)

5) verify (r, s, h, PubKey) is valid

You may use a library for point multiplication, but everything else you must do from scratch