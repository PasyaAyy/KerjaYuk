# KerjaYuk

Portal lowongan magang dan kerja paruh waktu untuk Tugas Besar 1 Komputasi Awan (DevOps & CI/CD Pipeline Jenkins), studi kasus K09.

> **Status:** backend MVP dan konfigurasi Docker awal tersedia. Rancangan lengkap ada di [`docs/architecture.md`](docs/architecture.md).

## Tim

| Nama | NIM | Peran | Tanggung jawab |
| --- | --- | --- | --- |
| Muhammad Brilliant Agung Wicaksono | 102062400126 | Tech Lead / Backend | Struktur project, REST API, aturan bisnis, dan migrasi database |
| Ahmad Nurtajalla Garda Islam | 102062400012 | DevOps Engineer | Setup Jenkins, webhook Ngrok, credentials, dan Jenkinsfile |
| Muhammad Naufal Syamdany | 102062400100 | Container Engineer | Dockerfile multi-stage, compose.yaml (3 service), dan .env |
| Pasya Ayu Rastiti | 102062400004 | QA & Tech Writer | Automated testing (minimal 5 test), laporan PDF, dan README.md |

## Teknologi pilihan awal

- Backend API: Python 3.12 dan FastAPI
- Database: PostgreSQL
- Reverse proxy: Nginx, port depan 8000
- Container: Docker dan Docker Compose
- CI/CD: Jenkins dan GitHub Webhook melalui Ngrok
- Detail arsitektur, skema data, dan rancangan endpoint: [`docs/architecture.md`](docs/architecture.md)

## Fitur wajib

- CRUD perusahaan dan lowongan kerja.
- Pencarian lowongan berdasarkan lokasi, tipe pekerjaan, dan kata kunci.
- Pengiriman lamaran dengan lampiran CV.
- Pengelolaan status lamaran dengan alur `DIKIRIM` → `DITINJAU` → `DITERIMA` atau `DITOLAK`.
- Endpoint `GET /health` untuk memeriksa server dan koneksi database.

## Aturan bisnis yang perlu diuji

- CV harus berupa PDF dengan ukuran maksimal 2 MB.
- Pelamar hanya dapat melamar satu kali pada lowongan yang sama.
- Lowongan yang sudah melewati tanggal berlaku tidak menerima lamaran baru.
- Perubahan status lamaran harus mengikuti alur yang ditentukan.
- Automated test mencakup minimal lima test.

## Penyimpanan CV

CV disimpan dalam Docker named volume `cv_data_volume` agar tetap tersedia setelah container dimulai ulang atau dibuat ulang.

## Menjalankan dengan Docker Compose

Salin `.env.example` menjadi `.env`, lalu jalankan:

```sh
docker compose up --build -d
```

API tersedia di `http://localhost:8000`; dokumentasi interaktif ada di `http://localhost:8000/docs`. Untuk menghentikan layanan, jalankan `docker compose down`. Data database dan CV tetap berada di named volume. Jangan gunakan password contoh di `.env` untuk deployment.

## Endpoint yang tersedia

- `GET /health`
- CRUD perusahaan pada `/api/v1/companies`
- CRUD dan pencarian lowongan pada `/api/v1/jobs`
- Pengajuan dan daftar lamaran pada `/api/v1/jobs/{job_id}/applications`
- Pembaruan status pada `/api/v1/applications/{application_id}/status`
