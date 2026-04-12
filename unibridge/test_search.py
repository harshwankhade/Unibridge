import urllib.request
import urllib.error
import json
import time

def print_result(name, data):
    print(f"\n--- {name} ---")
    print(json.dumps(data, indent=2))

# 1. /health
try:
    req = urllib.request.Request("http://localhost:8002/health")
    with urllib.request.urlopen(req) as res:
        print_result("Health Check", json.loads(res.read().decode("utf-8")))
except urllib.error.HTTPError as e:
    print("Health Error:", e.read().decode("utf-8"))

# Wait a bit for other services to be fully warm
time.sleep(2)

# 2. Search without auth (demo mode)
try:
    payload = {"query": "we have battery degradation in our EV fleet", "category": "solve"}
    req = urllib.request.Request("http://localhost:8002/search", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        summary = {
            "query": data.get("query"),
            "translated_query": data.get("translated_query"),
            "num_results": len(data.get("results", [])),
            "sample_result_keys": list(data.get("results", [{}])[0].keys()) if data.get("results") else []
        }
        print_result("Search without auth", summary)
except urllib.error.HTTPError as e:
    print("Search Without Auth Error:", e.read().decode("utf-8"))

# Get auth token
token = None
try:
    login_data = {"email": "industry@demo.com", "password": "demo1234"}
    req = urllib.request.Request("http://localhost:8001/login", data=json.dumps(login_data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        token = json.loads(res.read().decode("utf-8")).get("access_token")
except Exception as e:
    print("Failed to get auth token:", e)

# 3. Search with auth
if token:
    try:
        payload = {"query": "compare water purification technologies", "category": "benchmark"}
        req = urllib.request.Request("http://localhost:8002/search", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method="POST")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            summary = {
                "query": data.get("query"),
                "translated_query": data.get("translated_query"),
                "num_results": len(data.get("results", [])),
                "sample_result_keys": list(data.get("results", [{}])[0].keys()) if data.get("results") else []
            }
            print_result("Search with auth", summary)
    except urllib.error.HTTPError as e:
        print("Search With Auth Error:", e.read().decode("utf-8"))
