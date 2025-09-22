import uvicorn, os
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware  # noqa
from fastapi import FastAPI
from src.bunny_cdn import BunnyCdn
from dotenv import load_dotenv
from middlewares.cors import custom_cors_middleware

# from middlewares.auth import auth_middleware
from middlewares.lifespan import lifespan
from src.bunny_cdn import BunnyCdn

# from auth.claim import JWTTokenManager

load_dotenv()
bunny = BunnyCdn(
    os.getenv("BUNNY_HOST"),
    os.getenv("BUNNY_ZONE"),
    os.getenv("BUNNY_KEY"),
    os.getenv("BUNNY_CDN"),
    os.getenv("STREAM_KEY"),
)
# jwt = JWTTokenManager(secret_key=os.getenv("JWT_SECRET"))


app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(custom_cors_middleware)


from router.biohr8k import router as biohr8k_router
from router.common import router as common_router
from router.charity8k import router as charity8k_router
from router.auth import router as auth_router

app.include_router(auth_router)
app.include_router(biohr8k_router)
app.include_router(common_router)
app.include_router(charity8k_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # This means "listen on all network interfaces"
        debug=True,
        port=8001,  # This is the port number you want
        log_level="debug",
        timeout_keep_alive=300,
        limit_concurrency=50,
        limit_max_requests=1000,
        # These are important for large uploads:
        timeout_graceful_shutdown=300,
        backlog=1000,
    )
