import random
import hashlib
from sympy import isprime, mod_inverse

def generate_prime_candidate(length):
    p = random.getrandbits(length)
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=1024):
    p = 4
    while not isprime(p):
        p = generate_prime_candidate(length)
    return p

def generate_rsa_keys(bits=1024):
    p = generate_prime_number(bits // 2)
    q = generate_prime_number(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    d = mod_inverse(e, phi)

    return (e, n), (d, n)

def encrypt_rsa(private_key, plaintext):
    d, n = private_key
    plaintext_bytes = plaintext.encode('utf-8')
    plaintext_int = int.from_bytes(plaintext_bytes, byteorder='big')
    ciphertext_int = pow(plaintext_int, d, n)
    return ciphertext_int

def decrypt_rsa(public_key, ciphertext):
    e, n = public_key
    plaintext_int = pow(ciphertext, e, n)
    plaintext_bytes = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, byteorder='big')
    return plaintext_bytes.decode('utf-8')

def hash_username(username):
    return hashlib.sha256(username.encode('utf-8')).hexdigest()

def sign_rsa(private_key, username):
    username_hash = hash_username(username)
    return encrypt_rsa(private_key, username_hash)
