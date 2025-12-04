import json
import requests

student_id = "23P31A4274"  
github_repo_url = "https://github.com/prasad5682/pki-2fa-service"  
public_key_file = "keys/student_public.pem"  
api_url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


with open(public_key_file, "r") as f:
    public_key = f.read().strip()  

payload = {
    "student_id": student_id,
    "github_repo_url": github_repo_url,
    "public_key": public_key
}

print("Payload being sent to API:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(api_url, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print("Error calling API:", e)
    exit(1)

if data.get("status") == "success" and "encrypted_seed" in data:
    encrypted_seed = data["encrypted_seed"]
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)
    print("sucessfully Encrypted seed saved to encrypted_seed.txt")
else:
    print("API error:", data)
