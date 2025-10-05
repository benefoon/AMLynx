from __future__ import annotations
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from loguru import logger

from api.transactions.main import router as tx_router
from api.rules_engine.main import router as rules_router
from common.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# CORS (adjust to your frontend origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    with logger.contextualize(request_id=rid, path=request.url.path, method=request.method):
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

# Error handler (clean 500s)
@app.exception_handler(Exception)
async def unhandled_exc_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Routers
app.include_router(tx_router)
app.include_router(rules_router)

# Health & readiness
@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}

@app.get("/ready")
def ready():
    # optionally check DB connectivity, model file existence, etc.
    return {"ready": True}
