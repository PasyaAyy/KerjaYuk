from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database, main
from app.database import Base, get_db


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(connection, _):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
database.engine = engine
main.engine = engine


@pytest.fixture
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    if inspect(engine).has_table("alembic_version"):
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM alembic_version"))
    monkeypatch.setenv("CV_STORAGE_PATH", str(tmp_path / "cv"))

    def override_get_db():
        with TestingSession() as session:
            yield session

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def company_payload():
    return {
        "name": "RuangKreasi",
        "description": "Studio produk digital.",
        "location": "Bandung",
        "website": "https://ruangkreasi.example",
    }


@pytest.fixture
def create_company(client, company_payload):
    response = client.post("/api/v1/companies", json=company_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def create_job(client, create_company):
    from datetime import date, timedelta

    def create(**overrides):
        payload = {
            "company_id": create_company["id"],
            "title": "Product Design Intern",
            "description": "Membantu tim mengembangkan produk digital.",
            "location": "Bandung",
            "employment_type": "MAGANG",
            "expires_at": (date.today() + timedelta(days=60)).isoformat(),
        }
        payload.update(overrides)
        response = client.post("/api/v1/jobs", json=payload)
        assert response.status_code == 201
        return response.json()

    return create
