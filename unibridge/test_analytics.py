import urllib.request
import urllib.error
import json
import os

BASE_URL = "http://localhost:8005"

def send_request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    if data:
        data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "msg": e.read().decode()}

print("1. Testing /health")
print(send_request("/health"))

print("\n2. Logging test event 1")
event1 = {
    "user_id": 1,
    "query": "battery degradation in EVs",
    "translated_query": "electrochemical degradation lithium-ion",
    "category": "solve",
    "result_count": 8,
    "top_domains": ["Computing & AI", "Chemistry & Materials"],
    "top_universities": ["MIT", "Stanford University"]
}
print(send_request("/event", method="POST", data=event1))

print("\n3. Logging test event 2 (zero results)")
event2 = {
    "query": "fusion reactor plasma control",
    "category": "landscape",
    "result_count": 0,
    "top_domains": [],
    "top_universities": []
}
print(send_request("/event", method="POST", data=event2))

print("\n4. Checking /trending")
print(json.dumps(send_request("/trending"), indent=2))

print("\n5. Checking /gaps")
print(json.dumps(send_request("/gaps"), indent=2))

print("\n6. Checking /trl-distribution")
print(json.dumps(send_request("/trl-distribution"), indent=2))

print("\n7. Checking /category-breakdown")
print(json.dumps(send_request("/category-breakdown"), indent=2))

print("\n8. Checking /recent")
print(json.dumps(send_request("/recent"), indent=2))

print("\n9. Checking if analytics.db was created")
db_path = "services/analytics/analytics.db"
if os.path.exists(db_path):
    print("SUCCESS: analytics.db exists!")
else:
    print("FAILURE: analytics.db not found!")
