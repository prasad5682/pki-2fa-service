from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import pyotp
import time

app = FastAPI()

# ----------------------------
# File paths
# ----------------------------
PRIVATE_KEY_FILE = "keys/student_private.pem"  # Your private key path
SEED_FILE = "/data/seed.txt"                    # Where decrypted seed will be saved

# ----------------------------
# Load private key at startup
# ----------------------------
with open(PRIVATE_KEY_FILE, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# ----------------------------
# Pydantic models for request bodies
# ----------------------------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class Verify2FARequest(BaseModel):
    code: str

# ----------------------------
# Helper: decrypt encrypted seed
# ----------------------------
def decrypt_seed(encrypted_seed_b64: str) -> str:
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

    # Validate 64-character hex
    if len(decrypted_seed) != 64 or any(c not in "0123456789abcdef" for c in decrypted_seed.lower()):
        raise ValueError("Invalid decrypted seed")

    return decrypted_seed

# ----------------------------
# Endpoint 1: POST /decrypt-seed
# ----------------------------
@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request_data: DecryptSeedRequest):
    encrypted_seed = request_data.encrypted_seed

    try:
        seed = decrypt_seed(encrypted_seed)

        os.makedirs("/data", exist_ok=True)
        with open(SEED_FILE, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

# ----------------------------
# Helper: read seed from file
# ----------------------------
def read_seed() -> str:
    if not os.path.exists(SEED_FILE):
        raise Exception("Seed not decrypted yet")
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

# ----------------------------
# Helper: convert hex seed to base32
# ----------------------------
def hex_to_base32(hex_seed: str) -> str:
    return base64.b32encode(bytes.fromhex(hex_seed)).decode("utf-8")

# ----------------------------
# Endpoint 2: GET /generate-2fa
# ----------------------------
@app.get("/generate-2fa")
async def generate_2fa():
    try:
        hex_seed = read_seed()
        base32_seed = hex_to_base32(hex_seed)

        totp = pyotp.TOTP(base32_seed)
        code = totp.now()

        valid_for = 30 - (int(time.time()) % 30)

        return {"code": code, "valid_for": valid_for}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# Endpoint 3: POST /verify-2fa
# ----------------------------
@app.post("/verify-2fa")
async def verify_2fa(request_data: Verify2FARequest):
    code = request_data.code

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    try:
        hex_seed = read_seed()
        base32_seed = hex_to_base32(hex_seed)

        totp = pyotp.TOTP(base32_seed)

        # Verify with ±1 period tolerance
        valid = totp.verify(code, valid_window=1)

        return {"valid": valid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# Run: uvicorn api:app --reload
# ----------------------------
