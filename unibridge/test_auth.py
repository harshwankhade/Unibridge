import urllib.request
import urllib.error
import json
import uuid

base_url = "http://localhost:8001"

# 1. Register
print("--- [1] Testing /register ---")
unique_email = f"test_{uuid.uuid4().hex[:6]}@test.com"
register_data = {"email": unique_email, "password": "test1234", "role": "industry"}
req = urllib.request.Request(f"{base_url}/register", data=json.dumps(register_data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req) as res:
        print("Register response:", json.loads(res.read().decode("utf-8")))
except urllib.error.HTTPError as e:
    print("Register error:", e.read().decode("utf-8"))

# 2. Login
print("\n--- [2] Testing /login ---")
login_data = {"email": "industry@demo.com", "password": "demo1234"}
req = urllib.request.Request(f"{base_url}/login", data=json.dumps(login_data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
token = None
try:
    with urllib.request.urlopen(req) as res:
        response_json = json.loads(res.read().decode("utf-8"))
        print("Login response:", response_json)
        token = response_json.get("access_token")
except urllib.error.HTTPError as e:
    print("Login error:", e.read().decode("utf-8"))

# 3. Verify
print("\n--- [3] Testing /verify ---")
if token:
    req = urllib.request.Request(f"{base_url}/verify", headers={"Authorization": f"Bearer {token}"}, method="GET")
    try:
        with urllib.request.urlopen(req) as res:
            print("Verify response:", json.loads(res.read().decode("utf-8")))
    except urllib.error.HTTPError as e:
        print("Verify error:", e.read().decode("utf-8"))
else:
    print("Could not verify - no token obtained from login.")
