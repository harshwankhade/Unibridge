from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx
import os
from middleware import verify_token, check_role
from routes import match_route

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    
    # Allow any localhost port so Vite port fallbacks (3001, 5174, etc.) never break CORS
    allow_origins=["http://localhost:4000", "http://localhost:5173"],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Headers that must NOT be forwarded to downstream services
_SKIP_HEADERS = {"host", "content-length", "transfer-encoding"}

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}

# ---------------------------------------------------------------------------
# Universal proxy
# ---------------------------------------------------------------------------

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(path: str, request: Request):
    full_path = "/" + path

    # Handle CORS preflight immediately — never auth-check OPTIONS
    if request.method == "OPTIONS":
        return Response(status_code=200)

    # 1. Route matching
    route = match_route(full_path)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    # 2. Auth + role check for protected routes
    if not route["public"]:
        authorization = request.headers.get("authorization")
        payload = verify_token(authorization)       # raises 401 on failure
        check_role(payload, route["roles"])         # raises 403 on failure

    # 3. Build target URL
    if route["strip_prefix"]:
        # Remove the prefix from the path so /submission/submit → /submit
        remaining = full_path[len(route["prefix"]):]
        if not remaining:
            remaining = "/"
    else:
        remaining = full_path

    target_url = route["target"] + remaining

    # 4. Build forwarding headers (drop hop-by-hop headers)
    forward_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _SKIP_HEADERS
    }

    # 5. Read body and forward request
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=body,
                params=dict(request.query_params),
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail=f"Service unavailable: {route['prefix']}",
        )

    # 6. Return downstream response verbatim
    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
