import urllib.request
import urllib.error
import json
import time

def print_result(desc, res, status_only=False):
    print(f"\n--- {desc} ---")
    if hasattr(res, 'code'): 
        print(f"Status Code: {res.code}")
    if not status_only and hasattr(res, 'read'):
        try:
            print("Response:", json.loads(res.read().decode("utf-8")))
        except Exception:
            pass

base = "http://localhost:8000"

# Wait a bit to ensure all background models loaded
print("Waiting for ML models to load (15 seconds)...")
time.sleep(15)

try:
    with urllib.request.urlopen(urllib.request.Request(f"{base}/health")) as res:
        print_result("Health Check", res)
except urllib.error.HTTPError as e: print_result("Health Check", e)

# 1. Login Industry
ind_token = None
try:
    req = urllib.request.Request(f"{base}/auth/login", data=json.dumps({"email": "industry@demo.com", "password": "demo1234"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        ind_token = data.get("access_token")
        print(f"\n--- Login Industry ---\nStatus Code: {res.code}\nToken Acquired: {'Yes' if ind_token else 'No'}")
except urllib.error.HTTPError as e: print_result("Login Industry", e)

# 2. Login Admin
adm_token = None
try:
    req = urllib.request.Request(f"{base}/auth/login", data=json.dumps({"email": "admin@demo.com", "password": "demo1234"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        adm_token = data.get("access_token")
        print(f"\n--- Login Admin ---\nStatus Code: {res.code}\nToken Acquired: {'Yes' if adm_token else 'No'}")
except urllib.error.HTTPError as e: print_result("Login Admin", e)

# Register University
try:
    req = urllib.request.Request(f"{base}/auth/register", data=json.dumps({"email": "uni@demo.com", "password": "demo1234", "role": "university"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req).read()
except Exception: pass

uni_token = None
try:
    req = urllib.request.Request(f"{base}/auth/login", data=json.dumps({"email": "uni@demo.com", "password": "demo1234"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        uni_token = json.loads(res.read().decode()).get("access_token")
except urllib.error.HTTPError as e: pass

# 3. Industry hitting Search Data
try:
    req = urllib.request.Request(f"{base}/search/search", data=json.dumps({"query": "battery degradation", "category": "solve"}).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {ind_token}"}, method="POST")
    with urllib.request.urlopen(req) as res:
        print(f"\n--- Industry -> Search ---\nStatus Code: {res.code} (Success)")
except urllib.error.HTTPError as e: print_result("Industry -> Search", e, True)

# 4. Industry hitting Admin route
try:
    req = urllib.request.Request(f"{base}/admin/users", headers={"Authorization": f"Bearer {ind_token}"})
    with urllib.request.urlopen(req) as res: print_result("Industry -> Admin", res, True)
except urllib.error.HTTPError as e: print_result("Industry -> Admin Error Expected (403)", e, True)

# 5. University hitting Search route
try:
    req = urllib.request.Request(f"{base}/search/search", data=json.dumps({"query": "battery degradation", "category": "solve"}).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {uni_token}"}, method="POST")
    with urllib.request.urlopen(req) as res: print_result("University -> Search", res, True)
except urllib.error.HTTPError as e: print_result("University -> Search Error Expected (403)", e, True)

# 6. No Token hitting Search route
try:
    req = urllib.request.Request(f"{base}/search/search", data=json.dumps({"query": "test", "category": "solve"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res: print_result("No Token -> Search", res, True)
except urllib.error.HTTPError as e: print_result("No Token -> Search Error Expected (401)", e, True)

# 7. Admin token hitting Admin route (expect 502 since downstream Admin isn't running)
try:
    req = urllib.request.Request(f"{base}/admin/users", headers={"Authorization": f"Bearer {adm_token}"})
    with urllib.request.urlopen(req) as res: print_result("Admin -> Admin", res, True)
except urllib.error.HTTPError as e: print_result("Admin -> Admin Expected (502 if downstream offline, Else 200)", e, True)

print("\nGateway Routing Test Completed!")
