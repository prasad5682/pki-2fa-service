import base64
import pyotp

# Step 1: Convert hex seed to base32
def hex_to_base32(hex_seed: str) -> str:
    """Convert 64-character hex seed to base32 string"""
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    return base32_seed

# Step 2: Generate TOTP code
def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)  # 30s period, 6 digits
    return totp.now()  # Returns current 6-digit code as string

# Step 3: Verify TOTP code
def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)

# --- Example Usage ---
hex_seed = "c9a8331fd7cf85dec9bddda1d0a27873cb7197fc02b8847acdb0015502c5869c"  # From Step 5
totp_code = generate_totp_code(hex_seed)
print("Generated TOTP Code:", totp_code)

# Optional verification example
is_valid = verify_totp_code(hex_seed, totp_code)
print("Is TOTP valid?", is_valid)
