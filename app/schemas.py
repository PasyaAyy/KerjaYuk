from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EmploymentType(StrEnum):
    MAGANG = "MAGANG"
    PARUH_WAKTU = "PARUH_WAKTU"
    PENUH_WAKTU = "PENUH_WAKTU"


class ApplicationStatus(StrEnum):
    DIKIRIM = "DIKIRIM"
    DITINJAU = "DITINJAU"
    DITERIMA = "DITERIMA"
    DITOLAK = "DITOLAK"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(default=None, max_length=200)
    website: HttpUrl | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    location: str | None = Field(default=None, max_length=200)
    website: HttpUrl | None = None


class CompanyRead(ORMModel):
    id: int
    name: str
    description: str | None
    location: str | None
    website: str | None
    created_at: datetime


class JobCreate(BaseModel):
    company_id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    location: str = Field(min_length=1, max_length=200)
    employment_type: EmploymentType
    expires_at: date


class JobUpdate(BaseModel):
    company_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    employment_type: EmploymentType | None = None
    expires_at: date | None = None


class JobRead(ORMModel):
    id: int
    company_id: int
    title: str
    description: str
    location: str
    employment_type: EmploymentType
    expires_at: date
    created_at: datetime


class ApplicationRead(ORMModel):
    id: int
    job_id: int
    applicant_id: int
    cv_path: str
    status: ApplicationStatus
    applied_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
