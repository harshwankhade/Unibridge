import urllib.request
import urllib.error
import json
import os
import sys

BASE_URL = "http://localhost:8004"
AUTH_URL = "http://localhost:8001"

def do_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def test_submission():
    print("1. Logging in as university...")
    status, res = do_request(f"{AUTH_URL}/login", method="POST", data={"email": "university@demo.com", "password": "demo1234"})
    if status != 200:
        print(f"Failed to login: {res}")
        sys.exit(1)
           
    uni_token = res["access_token"]
    print(f"Got university token.")

    print("\n2. Health check...")
    status, res = do_request(f"{BASE_URL}/health")
    print(f"Health response: {res}")

    print("\n3. Submit a record...")
    headers = {"Authorization": f"Bearer {uni_token}"}
    payload = {
        "title": "Novel carbon capture membrane",
        "abstract": "A new polymer membrane that captures CO2 with 90% efficiency.",
        "university": "IIT Bombay",
        "contributors": "Dr. Sharma, Dr. Patel",
        "domain": "Environmental Science",
        "ip_type": "patent",
        "legal_status": "ACTIVE"
    }
    status, res = do_request(f"{BASE_URL}/submit", method="POST", data=payload, headers=headers)
    print(f"Submit response: {res}")
    submission_id = res.get("submission_id")

    print("\n4. List submissions as university...")
    status, res = do_request(f"{BASE_URL}/submissions", headers=headers)
    print(f"List response: {res}")

    print("\n5. Logging in as admin...")
    status, res = do_request(f"{AUTH_URL}/login", method="POST", data={"email": "admin@demo.com", "password": "demo1234"})
    admin_token = res["access_token"]
    print("Got admin token.")
    
    print("\n6. List submissions as admin...")
    status, res = do_request(f"{BASE_URL}/submissions", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"Admin list response: total={res.get('total')}")

    print(f"\n7. Approving submission {submission_id}...")
    status, res = do_request(f"{BASE_URL}/submissions/{submission_id}/approve", 
                             method="POST",
                             data={"admin_note": "Approved for indexing"}, 
                             headers={"Authorization": f"Bearer {admin_token}"})
    print(f"Approve response: {res}")

    db_path = "services/submission/submission.db"
    print(f"\n8. Checking if {db_path} exists...")
    if os.path.exists(db_path):
        print("submission.db exists! Test completely successful.")
    else:
        print("submission.db NOT FOUND! Test failed.")

if __name__ == '__main__':
    test_submission()
