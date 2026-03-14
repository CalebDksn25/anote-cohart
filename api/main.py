import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import extract, evaluate
from api.exceptions import unhandled_exception_handler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        raise RuntimeError(
            "OPENAI_API_KEY is missing or invalid. "
            "Set it in your .env file before starting the server."
        )
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="anote-cohart API", version="1.0.0", lifespan=lifespan)

    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(extract.router, prefix="/api")
    app.include_router(evaluate.router, prefix="/api")

    return app


app = create_app()
