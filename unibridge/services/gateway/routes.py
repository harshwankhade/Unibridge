import os

ROUTES = [
    {
        "prefix":       "/auth",
        "target":       os.environ.get("AUTH_URL",       "http://localhost:8001"),
        "strip_prefix": True,
        "public":       True,   # no token required
        "roles":        [],
    },
    {
        "prefix":       "/search",
        "target":       os.environ.get("SEARCH_URL",     "http://localhost:8002"),
        "strip_prefix": False,
        "public":       False,
        "roles":        ["industry", "admin"],
    },
    {
        "prefix":       "/data",
        "target":       os.environ.get("DATA_URL",       "http://localhost:8003"),
        "strip_prefix": True,
        "public":       False,
        "roles":        ["admin"],
    },
    {
        "prefix":       "/submission",
        "target":       os.environ.get("SUBMISSION_URL", "http://localhost:8004"),
        "strip_prefix": True,
        "public":       False,
        "roles":        ["university", "admin"],
    },
    {
        "prefix":       "/analytics",
        "target":       os.environ.get("ANALYTICS_URL",  "http://localhost:8005"),
        "strip_prefix": True,
        "public":       False,
        "roles":        ["admin"],
    },
    {
        "prefix":       "/admin",
        "target":       os.environ.get("ADMIN_URL",      "http://localhost:8006"),
        "strip_prefix": True,
        "public":       False,
        "roles":        ["admin"],
    },
]


def match_route(path: str) -> dict | None:
    """Return the first route whose prefix matches the start of `path`."""
    for route in ROUTES:
        if path.startswith(route["prefix"]):
            return route
    return None
