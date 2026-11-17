"""Insert synthetic companies and vacancies for a local demonstration."""

from datetime import date, timedelta

from sqlalchemy import select

from app.database import SessionLocal, engine
from app.migrations import upgrade_database
from app.models import Company, Job


def seed_demo_data() -> tuple[int, int]:
    """Create the demo catalog once, without replacing existing records."""
    upgrade_database(engine)
    samples = [
        {
            "company": {"name": "RuangKreasi Labs", "location": "Bandung"},
            "jobs": [
                {
                    "title": "Product Design Intern",
                    "description": "Berkolaborasi dengan tim produk untuk merancang pengalaman digital yang mudah digunakan.",
                    "location": "Bandung · Hybrid",
                    "employment_type": "MAGANG",
                },
                {
                    "title": "Frontend Developer Intern",
                    "description": "Membangun antarmuka web yang aksesibel bersama engineer dan designer.",
                    "location": "Bandung · Remote",
                    "employment_type": "MAGANG",
                },
            ],
        },
        {
            "company": {"name": "TemanBelajar", "location": "Jakarta"},
            "jobs": [
                {
                    "title": "Content Creator Intern",
                    "description": "Membantu merencanakan dan membuat konten edukasi untuk komunitas pembelajar.",
                    "location": "Jakarta · Remote",
                    "employment_type": "MAGANG",
                }
            ],
        },
        {
            "company": {"name": "Kopi & Cerita", "location": "Depok"},
            "jobs": [
                {
                    "title": "Admin Operasional Paruh Waktu",
                    "description": "Mendukung kegiatan operasional harian dan layanan pelanggan.",
                    "location": "Depok · On-site",
                    "employment_type": "PARUH_WAKTU",
                }
            ],
        },
    ]
    companies_created = 0
    jobs_created = 0
    expires_at = date.today() + timedelta(days=90)

    with SessionLocal() as session:
        for sample in samples:
            company_data = sample["company"]
            company = session.scalar(
                select(Company).where(Company.name == company_data["name"])
            )
            if company is None:
                company = Company(**company_data)
                session.add(company)
                session.flush()
                companies_created += 1

            for job_data in sample["jobs"]:
                exists = session.scalar(
                    select(Job.id).where(
                        Job.company_id == company.id,
                        Job.title == job_data["title"],
                    )
                )
                if exists is None:
                    session.add(Job(company_id=company.id, expires_at=expires_at, **job_data))
                    jobs_created += 1

        session.commit()

    return companies_created, jobs_created


if __name__ == "__main__":
    companies, jobs = seed_demo_data()
    print(f"Data demo siap: {companies} perusahaan dan {jobs} lowongan baru.")
