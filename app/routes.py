import os
import re
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Applicant, Application, Company, Job
from app.schemas import (
    ApplicationRead,
    ApplicationStatus,
    ApplicationStatusUpdate,
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
    EmploymentType,
    JobCreate,
    JobRead,
    JobUpdate,
)

router = APIRouter(prefix="/api/v1")
MAX_CV_SIZE = 2 * 1024 * 1024
VALID_TRANSITIONS = {
    ApplicationStatus.DIKIRIM: {ApplicationStatus.DITINJAU},
    ApplicationStatus.DITINJAU: {ApplicationStatus.DITERIMA, ApplicationStatus.DITOLAK},
}


@router.get("/companies", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return db.scalars(select(Company).order_by(Company.id)).all()


@router.post("/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**payload.model_dump(mode="json"))
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/companies/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    return company


@router.patch("/companies/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    db.delete(company)
    db.commit()


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(
    q: str | None = Query(default=None, min_length=1),
    location: str | None = Query(default=None, min_length=1),
    employment_type: EmploymentType | None = None,
    include_expired: bool = False,
    db: Session = Depends(get_db),
):
    statement = select(Job).order_by(Job.id)
    if not include_expired:
        statement = statement.where(Job.expires_at >= date.today())
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(or_(Job.title.ilike(pattern), Job.description.ilike(pattern)))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location.strip()}%"))
    if employment_type:
        statement = statement.where(Job.employment_type == employment_type.value)
    return db.scalars(statement).all()


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    if db.get(Company, payload.company_id) is None:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    return job


@router.patch("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("company_id") is not None and db.get(Company, updates["company_id"]) is None:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    for key, value in updates.items():
        setattr(job, key, value.value if isinstance(value, EmploymentType) else value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    db.delete(job)
    db.commit()


@router.post(
    "/jobs/{job_id}/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_job(
    job_id: int,
    name: str = Form(min_length=1, max_length=200),
    email: str = Form(min_length=3, max_length=320),
    cv: UploadFile = File(),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    if job.expires_at < date.today():
        raise HTTPException(status_code=409, detail="Lowongan sudah kedaluwarsa")

    normalized_email = email.strip().casefold()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized_email):
        raise HTTPException(status_code=422, detail="Format email tidak valid")
    applicant = db.scalar(select(Applicant).where(Applicant.email == normalized_email))
    if applicant and db.scalar(
        select(Application.id).where(
            Application.job_id == job_id, Application.applicant_id == applicant.id
        )
    ):
        raise HTTPException(status_code=409, detail="Pelamar sudah melamar lowongan ini")

    if cv.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="CV harus berupa file PDF")
    contents = await cv.read(MAX_CV_SIZE + 1)
    if len(contents) > MAX_CV_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran CV maksimal 2 MB")
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Isi file bukan PDF yang valid")

    storage_dir = Path(os.getenv("CV_STORAGE_PATH", "./data/cv"))
    storage_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.pdf"
    stored_path = storage_dir / stored_name
    stored_path.write_bytes(contents)
    try:
        if applicant is None:
            applicant = Applicant(name=name.strip(), email=normalized_email)
            db.add(applicant)
            db.flush()
        application = Application(
            job_id=job_id,
            applicant_id=applicant.id,
            cv_path=stored_name,
            status=ApplicationStatus.DIKIRIM.value,
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    except IntegrityError as exc:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="Pelamar sudah melamar lowongan ini") from exc
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise


@router.get("/jobs/{job_id}/applications", response_model=list[ApplicationRead])
def list_applications(job_id: int, db: Session = Depends(get_db)):
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    return db.scalars(
        select(Application).where(Application.job_id == job_id).order_by(Application.id)
    ).all()


@router.patch("/applications/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    current_status = ApplicationStatus(application.status)
    if payload.status not in VALID_TRANSITIONS.get(current_status, set()):
        raise HTTPException(status_code=409, detail="Transisi status lamaran tidak valid")
    application.status = payload.status.value
    db.commit()
    db.refresh(application)
    return application
