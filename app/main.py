from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import models  # noqa: F401 - registers models with Base metadata
from app.database import engine
from app.migrations import upgrade_database
from app.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    upgrade_database(engine)
    yield


app = FastAPI(
    title="KerjaYuk API",
    description="REST API portal lowongan magang dan kerja paruh waktu.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/health", tags=["health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database tidak tersedia") from exc
    return {"status": "ok", "database": "ok"}
