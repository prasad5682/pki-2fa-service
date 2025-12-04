import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

private_key_file = "keys/student_private.pem"
with open(private_key_file, "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)


    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    
    decrypted_seed = decrypted_bytes.decode("utf-8")

    
    if len(decrypted_seed) != 64 or any(c not in "0123456789abcdef" for c in decrypted_seed):
        raise ValueError("Decrypted seed is not a valid 64-character hex string")

    
    return decrypted_seed


seed = decrypt_seed(encrypted_seed_b64, private_key)
print("Decrypted Seed:", seed)


with open("/data/seed.txt", "w") as f:

    f.write(seed)
