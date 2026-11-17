# Laporan Proyek KerjaYuk

## Ringkasan

KerjaYuk adalah portal MVP untuk menemukan lowongan magang dan kerja paruh waktu. Proyek menggabungkan frontend web responsif, REST API FastAPI, PostgreSQL, Nginx, Docker Compose, tes otomatis, dan pipeline Jenkins.

## Identitas proyek

- Mata kuliah: Komputasi Awan (DevOps & CI/CD Pipeline Jenkins)
- Studi kasus: K09
- Tim: Muhammad Brilliant Agung Wicaksono (102062400126), Ahmad Nurtajalla Garda Islam (102062400012), Muhammad Naufal Syamdany (102062400100), dan Pasya Ayu Rastiti (102062400004).

## Tujuan dan ruang lingkup

Pengguna dapat mencari lowongan berdasarkan kata kunci, lokasi, dan tipe pekerjaan, lalu mengirim lamaran beserta CV PDF. Perusahaan dapat dicatat dan lowongan dapat dibuat melalui endpoint API atau formulir web demo. Pengelola dapat mengubah status lamaran mengikuti alur yang ditentukan.

## Arsitektur

Browser memuat frontend statis dari Nginx. Nginx meneruskan permintaan `/api/*`, `/health`, dan dokumentasi API ke FastAPI. API mengakses PostgreSQL melalui SQLAlchemy. Berkas CV disimpan pada named volume Docker terpisah agar tidak hilang saat container dibuat ulang.

Compose menjalankan tiga service: `nginx`, `api`, dan `db`. Health check PostgreSQL mencegah API dimulai sebelum database siap. API menerapkan migrasi Alembic ketika mulai; migrasi awal juga mengadopsi database MVP lama yang sudah mempunyai seluruh tabel inti. Health check API dipakai untuk memeriksa konektivitas database; Nginx juga menyediakan endpoint health melalui proxy.

## Fitur dan aturan bisnis

- CRUD perusahaan dan lowongan.
- Pencarian berdasarkan judul/deskripsi, lokasi, dan tipe kerja.
- Lowongan kedaluwarsa disembunyikan dari hasil default dan tidak menerima lamaran.
- CV harus PDF, memiliki magic header PDF, dan berukuran paling banyak 2 MiB.
- Email pelamar dinormalisasi dan pelamar yang sama tidak dapat mengirim lamaran dua kali untuk lowongan yang sama.
- Status lamaran bergerak dari `DIKIRIM` ke `DITINJAU`, lalu ke `DITERIMA` atau `DITOLAK`.
- Endpoint `/health` mengecek server dan koneksi database.

## Pengujian

Tes API menggunakan SQLite sementara dan FastAPI TestClient. Cakupan mencakup health check, CRUD perusahaan, pencarian/filter lowongan, pengiriman CV valid, penolakan berkas non-PDF dan berukuran lebih dari 2 MiB, lamaran duplikat, lowongan kedaluwarsa, serta transisi status lamaran. Jenkins menerbitkan hasil pytest sebagai laporan JUnit.

## CI/CD

Jenkinsfile menjalankan checkout, pemasangan dependensi tes, lint Ruff, kompilasi Python, tes, dan build container. Deploy Compose hanya berjalan pada branch `main` saat parameter `DEPLOY` dipilih. GitHub webhook dapat memicu Multibranch Pipeline melalui GitHub Branch Source; Ngrok dipakai untuk mengekspos Jenkins lokal selama demo.

Urutan stage pipeline: **Checkout → Install dependencies → Lint/compile → Pytest/JUnit → Build laporan PDF → Build image Docker → Deploy Compose opsional pada `main`**.

## Pembagian peran dan bukti yang dilampirkan

| Anggota | Peran dan tanggung jawab | Bukti laporan |
| --- | --- | --- |
| Muhammad Brilliant Agung Wicaksono (102062400126) | Tech Lead / Backend: struktur project, endpoint, aturan bisnis, migrasi, dan seeder | Kode fitur inti dan tautan pull request backend yang sudah di-merge |
| Ahmad Nurtajalla Garda Islam (102062400012) | DevOps Engineer: Jenkins, webhook/Ngrok, credentials, dan Jenkinsfile | Konfigurasi job, Stage View, serta console log Jenkins |
| Muhammad Naufal Syamdany (102062400100) | Container Engineer: Dockerfile, Compose, `.env.example`, dan health checks | Konfigurasi file dan output `docker compose ps` |
| Pasya Ayu Rastiti (102062400004) | QA Engineer & Tech Writer: unit/feature tests, skenario pipeline gagal-pulih, README, diagram pipeline, dan laporan | File test, bukti pipeline merah lalu hijau, README, diagram, serta laporan PDF |

Status bukti pada 17 November 2026: baseline implementasi sudah tersedia di PR #1 menuju `main`, tetapi PR masih menunggu pemilik repo. Docker Compose menjalankan `nginx`, `api`, dan `db`; health API mengembalikan status OK. Pengujian lokal menghasilkan 12 tes lulus, Ruff lulus, dan kompilasi Python lulus. Jenkins lokal dapat dibuka. GitHub telah menerima webhook `ping` dengan HTTP 200, tetapi ping tidak menjalankan pipeline dan belum ada bukti build Jenkins untuk push terbaru. Commit anggota lain, screenshot Stage View/console, dan bukti build gagal lalu pulih harus berasal dari pekerjaan serta eksekusi mereka sendiri.

## Menjalankan demo

Salin `.env.example` menjadi `.env`, jalankan `docker compose up --build -d`, kemudian opsional jalankan `docker compose exec api python -m app.seed`. Portal tersedia di `http://localhost:8000`, sedangkan dokumentasi API di `/docs`.

## Batasan dan pengembangan lanjutan

MVP belum memiliki autentikasi, role-based access, pagination, atau endpoint unduh CV. Karena itu, semua endpoint admin terbuka untuk demo lokal dan aplikasi tidak boleh dipublikasikan tanpa menambahkan kontrol akses serta pembatasan unduhan CV. Pengembangan berikutnya dapat menambah login perusahaan, dashboard status lamaran, dan deployment production dengan secret manager.
