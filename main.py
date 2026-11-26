import httpx  # async-capable HTTP client (requests can't do await)
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants in UPPER_SNAKE_CASE, one place to change (like #define / constexpr)
EXTERNAL_URL = "https://jsonplaceholder.typicode.com/posts"
EXTERNAL_TIMEOUT_SECONDS = 5.0  # NEVER call an external API without a timeout


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Day 4 catch-all: clean JSON instead of a raw traceback
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}  # tiny endpoint we use to prove the loop is free


# ===== DAY 5 =====
@app.get("/external")
async def get_external(limit: int = 5):  # `async def` = coroutine, can use await inside
    params = {"_limit": limit}  # query string: ?_limit=5 (httpx builds it for you)

    try:
        # `async with` = RAII for async resources: client opens here, closes
        # automatically on exit, even on exception (like a C++ scoped object)
        async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT_SECONDS) as client:
            # `await` = "pause this request until the network replies; let
            # other requests run meanwhile" (co_await)
            response = await client.get(EXTERNAL_URL, params=params)

            # Turns 4xx/5xx into an exception. Without it, a failed call
            # looks like a success and you parse garbage.
            response.raise_for_status()

            posts = response.json()  # parsed JSON -> Python list of dicts (sync, instant)

    except httpx.TimeoutException:  # upstream too slow -> 504 Gateway Timeout
        raise HTTPException(status_code=504, detail="External API timed out")
    except httpx.HTTPStatusError as exc:  # upstream replied with an error code
        raise HTTPException(
            status_code=502,  # 502 Bad Gateway = "the server behind me failed"
            detail=f"External API returned {exc.response.status_code}",
        )
    except httpx.RequestError:  # DNS failure, refused connection, etc.
        raise HTTPException(status_code=502, detail="Could not reach external API")

    # Return YOUR shape, not the raw upstream payload (don't leak upstream structure)
    return {
        "source": "jsonplaceholder",
        "count": len(posts),
        "posts": [{"id": p["id"], "title": p["title"]} for p in posts],
    }


