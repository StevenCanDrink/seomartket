from fastapi import Request, responses
import os

skip_paths = (
    "/api/docs",
    "/api/openapi.json",
    "/api/redoc",
    "/charity8k/upload-status",
    "/common/check-health",
)


async def custom_cors_middleware(request: Request, call_next):
    mode = os.getenv("MODE", "PRODUCTION")
    # Define your CORS configuration
    if (
        request.url.path.startswith(skip_paths)
        or request.headers.get("sec-fetch-site") == "same-origin"
    ):
        return await call_next(request)
    allowed_origins = [
        "https://bio.tuyendung8k.com",
        "https://bunny-cdn.live18k.me",
        "http://bio-helper-env.eba-azn2ehxh.ap-southeast-1.elasticbeanstalk.com",
        "http://localhost:8080",
        "https://media8k.net",
    ]

    allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allowed_headers = ["Content-Type", "Authorization", "X-Requested-With"]

    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = responses.JSONResponse(
            content={"message": "Preflight request successful"}, status_code=200
        )
    else:
        response = await call_next(request)

    # Add CORS headers
    origin = request.headers.get("origin")
    if mode == "PRODUCTION" and origin not in allowed_origins:
        return responses.JSONResponse(
            content={"message": "cors are not allowed"}, status_code=500
        )

    if origin and origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    elif "*" in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = "*"

    response.headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)

    return response
