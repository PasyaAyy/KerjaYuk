from datetime import date, timedelta

from sqlalchemy import text

from app.database import engine
from app.migrations import upgrade_database


def valid_resume():
    return ("resume.pdf", b"%PDF-1.4\nKerjaYuk test resume", "application/pdf")


def submit_application(client, job_id, *, email="ayu@example.com", resume=None):
    return client.post(
        f"/api/v1/jobs/{job_id}/applications",
        data={"name": "Ayu Rastiti", "email": email},
        files={"cv": resume or valid_resume()},
    )


def test_health_reports_database_connection(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_initial_schema_migration_is_recorded(client):
    with engine.connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert revision == "0001_initial"


def test_migration_adopts_existing_mvp_tables_without_losing_data(client, company_payload):
    created = client.post("/api/v1/companies", json=company_payload).json()
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE alembic_version"))

    upgrade_database(engine)

    assert client.get(f"/api/v1/companies/{created['id']}").json()["name"] == company_payload["name"]


def test_company_crud(client, company_payload):
    created = client.post("/api/v1/companies", json=company_payload)
    assert created.status_code == 201
    company_id = created.json()["id"]

    assert client.get(f"/api/v1/companies/{company_id}").json()["name"] == "RuangKreasi"
    updated = client.patch(f"/api/v1/companies/{company_id}", json={"name": "Ruang Kreatif"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Ruang Kreatif"
    assert client.delete(f"/api/v1/companies/{company_id}").status_code == 204
    assert client.get(f"/api/v1/companies/{company_id}").status_code == 404


def test_job_search_filters_keyword_location_type_and_expired(client, create_job):
    create_job()
    create_job(
        title="Part-time Content Writer",
        description="Menulis konten untuk pembaca.",
        location="Jakarta",
        employment_type="PARUH_WAKTU",
    )
    create_job(title="Arsip lama", expires_at=(date.today() - timedelta(days=1)).isoformat())

    assert len(client.get("/api/v1/jobs?q=Design").json()) == 1
    assert len(client.get("/api/v1/jobs?location=jakarta").json()) == 1
    part_time = client.get("/api/v1/jobs?employment_type=PARUH_WAKTU").json()
    assert [job["title"] for job in part_time] == ["Part-time Content Writer"]
    assert len(client.get("/api/v1/jobs").json()) == 2
    assert len(client.get("/api/v1/jobs?include_expired=true").json()) == 3


def test_job_crud(client, create_job):
    job = create_job()
    job_id = job["id"]

    assert client.get(f"/api/v1/jobs/{job_id}").json()["title"] == "Product Design Intern"
    updated = client.patch(f"/api/v1/jobs/{job_id}", json={"title": "Product Designer Intern"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Product Designer Intern"
    assert client.delete(f"/api/v1/jobs/{job_id}").status_code == 204
    assert client.get(f"/api/v1/jobs/{job_id}").status_code == 404


def test_application_accepts_valid_pdf_and_saves_file(client, create_job, tmp_path):
    job = create_job()

    response = submit_application(client, job["id"])

    assert response.status_code == 201
    application = response.json()
    assert application["status"] == "DIKIRIM"
    assert application["cv_path"].endswith(".pdf")
    stored_file = tmp_path / "cv" / application["cv_path"]
    assert stored_file.read_bytes().startswith(b"%PDF-")


def test_application_rejects_non_pdf(client, create_job):
    job = create_job()

    response = submit_application(
        client,
        job["id"],
        resume=("resume.txt", b"not a pdf", "text/plain"),
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_application_rejects_pdf_larger_than_two_megabytes(client, create_job):
    job = create_job()
    oversized_pdf = b"%PDF-1.4\n" + b"x" * (2 * 1024 * 1024)

    response = submit_application(
        client,
        job["id"],
        resume=("large.pdf", oversized_pdf, "application/pdf"),
    )

    assert response.status_code == 400
    assert "2 MB" in response.json()["detail"]


def test_duplicate_application_is_rejected_case_insensitively(client, create_job):
    job = create_job()
    first = submit_application(client, job["id"], email="ayu@example.com")
    duplicate = submit_application(client, job["id"], email=" AYU@EXAMPLE.COM ")

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_expired_job_rejects_application(client, create_job):
    job = create_job(expires_at=(date.today() - timedelta(days=1)).isoformat())

    response = submit_application(client, job["id"])

    assert response.status_code == 409
    assert "kedaluwarsa" in response.json()["detail"]


def test_application_status_must_follow_allowed_transitions(client, create_job):
    job = create_job()
    application = submit_application(client, job["id"]).json()
    application_id = application["id"]

    skipped = client.patch(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "DITERIMA"},
    )
    reviewed = client.patch(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "DITINJAU"},
    )
    accepted = client.patch(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "DITERIMA"},
    )

    assert skipped.status_code == 409
    assert reviewed.status_code == 200
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "DITERIMA"
