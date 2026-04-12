import urllib.request
import urllib.error
import json
import socket

ADMIN_URL = "http://localhost:8006"
AUTH_URL = "http://localhost:8001"

def send_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data:
        data = json.dumps(data).encode("utf-8")
        headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
    else:
        req = urllib.request.Request(url, method=method, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()
    except Exception as e:
        return 500, str(e)


# Setup tokens
print("0. Getting tokens...")
st, admin_res = send_request(f"{AUTH_URL}/login", "POST", {"email": "admin@demo.com", "password": "demo1234"})
admin_token = admin_res.get("access_token")

st, uni_res = send_request(f"{AUTH_URL}/login", "POST", {"email": "university@demo.com", "password": "demo1234"})
uni_token = uni_res.get("access_token")

# Health
print("\n1. Health Check")
print(send_request(f"{ADMIN_URL}/health")[1])

# Auth constraints on admin proxy
print("\n2. Checking Auth Constraints")
st, res = send_request(f"{ADMIN_URL}/users")
print(f"No token: HTTP {st} -> {res}")

st, res = send_request(f"{ADMIN_URL}/users", headers={"Authorization": f"Bearer {uni_token}"})
print(f"Non-admin token: HTTP {st} -> {res}")

# Downstream happy paths
print("\n3. Testing downstream proxies with Admin Token")
headers = {"Authorization": f"Bearer {admin_token}"}

print("Fetching Users...")
st, res = send_request(f"{ADMIN_URL}/users", headers=headers)
print(f"Users HTTP {st}: returned {len(res) if isinstance(res, list) else len(res.get('users', []))} users")

print("Fetching Submissions...")
st, res = send_request(f"{ADMIN_URL}/submissions", headers=headers)
# Submissions returns dict with "submissions" list
print(f"Submissions HTTP {st}: returned {len(res.get('submissions', [])) if isinstance(res, dict) else res} submissions")

print("Analytics Trending...")
st, res = send_request(f"{ADMIN_URL}/analytics/trending", headers=headers)
print(f"Trending HTTP {st}: {res}")

print("Analytics Gaps...")
st, res = send_request(f"{ADMIN_URL}/analytics/gaps", headers=headers)
print(f"Gaps HTTP {st}: {res}")

print("Analytics Recent...")
st, res = send_request(f"{ADMIN_URL}/analytics/recent", headers=headers)
# Recent returns dict with "recent"
print(f"Recent HTTP {st}: {len(res.get('recent', [])) if isinstance(res, dict) else res} recent events")

print("Data Stats...")
st, res = send_request(f"{ADMIN_URL}/data/stats", headers=headers)
if st == 502:
    print(f"Data stats HTTP {st} -> Server likely down, fulfilling the 502 test! Response: {res}")
else:
    print(f"Data stats HTTP {st} -> {res}")

# Force a 502 explicitly by giving a bad URL or if Data was down, we already showed it.
# To ensure we hit a 502, let's look at Data Stats if it succeeded.
