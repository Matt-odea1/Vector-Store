# src/app.py
from __future__ import annotations

import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

# Load env (local.env or .env at repo root)
load_dotenv(find_dotenv(filename="../local.env", usecwd=True), override=False)

# ✅ Correct import path for your router
from main.controllers.InternalEndpoints import router as context_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=os.getenv("APP_TITLE", "Context API"),
        version=os.getenv("APP_VERSION", "0.1.0"),
        docs_url=os.getenv("DOCS_URL", "/docs"),
        redoc_url=os.getenv("REDOC_URL", "/redoc"),
        openapi_url=os.getenv("OPENAPI_URL", "/openapi.json"),
    )

    # Optional CORS
    origins_env = os.getenv("ALLOW_ORIGINS", "")
    if origins_env:
        origins: List[str] = [o.strip() for o in origins_env.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Health/meta
    @app.get("/", tags=["meta"])
    def root():
        return {"ok": True, "service": "Context API"}

    @app.get("/healthz", tags=["meta"])
    def healthz():
        return {"status": "ok"}

    # ✅ Mount your internal router
    app.include_router(context_router)

    return app

# Module-level app for uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    # Use an import string for reload
    uvicorn.run("src.app:app", host=host, port=port, reload=reload)
