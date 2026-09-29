from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from .config import get_settings

from .database import init_db

from .routers import (
    auth,
    pages,
    recommendations,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    init_db()

    yield


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static",
)


app.include_router(
    pages.router
)

app.include_router(
    auth.router
)

app.include_router(
    recommendations.router
)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.get("/startup")
def startup():

    return {
        "status": "initialized",

        "ai_enabled": settings.ai_enabled,

        "model": settings.gemini_model,
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )