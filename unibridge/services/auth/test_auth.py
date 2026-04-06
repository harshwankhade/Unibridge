"""Quick in-process test of the auth FastAPI app."""
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from main import app

client = TestClient(app)

# 1. Health
r = client.get("/health")
print("Health:", r.status_code, r.json())

# 2. Login with known credentials
r2 = client.post("/login", json={"email": "industry@demo.com", "password": "demo1234"})
print("Login:", r2.status_code, r2.text[:200])

# 3. Register a fresh user
r3 = client.post("/register", json={"email": "testuser99@demo.com", "password": "pass1234", "role": "industry"})
print("Register:", r3.status_code, r3.text[:200])
