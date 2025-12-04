import base64
import pyotp
import datetime
import os

seed_path = "/data/seed.txt"
log_path = "/cron/last_code.txt"

try:
    if not os.path.exists(seed_path):
        raise Exception("Seed not found")

    with open(seed_path, "r") as f:
        hex_seed = f.read().strip()

    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a") as f:
        f.write(f"{timestamp} - 2FA Code: {code}\n")

except Exception as e:
    with open(log_path, "a") as f:
        f.write(f"ERROR: {str(e)}\n")
