KerjaYuk – Portal Lowongan Magang & Kerja Paruh Waktu
Tugas Besar 1 Komputasi Awan (DevOps & CI/CD Pipeline Jenkins)

Studi Kasus: K09 – KerjaYuk
👥 Anggota Kelompok & Pembagian Peran
Nama Anggota	NIM	Peran Utama	Tanggung Jawab Utama
Muhammad Brilliant Agung Wicaksono	[102062400126]	Tech Lead / Backend	Struktur project, REST API, aturan bisnis, dan migrasi database
Ahmad Nurtajalla Garda Islam [102062400012]	DevOps Engineer	Setup Jenkins, Webhook Ngrok, Credentials, dan Jenkinsfile
Muhammad Naufal Syamdany	[102062400100]	Container Engineer	Dockerfile multi-stage, compose.yaml (3 service), dan .env
Pasya Ayu Rastiti	[102062400004]	QA & Tech Writer	Automated testing (minimal 5 test), laporan PDF, dan README.md

🛠️ Tech Stack
Teknologi yang digunakan dalam pengembangan aplikasi KerjaYuk:
Backend Framework: [Contoh: Express.js / Laravel / FastAPI / Spring Boot]
Database: [Contoh: PostgreSQL / MySQL]
Reverse Proxy: Nginx (Front-facing port 8000)
Containerization: Docker & Docker Compose
CI/CD Pipeline: Jenkins + GitHub Webhook (via Ngrok)

🚀 Fitur Utama & Aturan Bisnis
Fitur Wajib
CRUD Perusahaan & Lowongan: Pengelolaan data perusahaan dan posting lowongan pekerjaan.
Pencarian & Filter: Pencarian lowongan berdasarkan lokasi, tipe pekerjaan, dan kata kunci.
Unggah CV & Melamar: Pengiriman lamaran pekerjaan dengan melampirkan file CV.
Manajemen Status: Pembaruan status lamaran dengan alur DIKIRIM → DITINJAU → DITERIMA / DITOLAK.
Health Check Endpoint: Endpoint GET /health untuk memverifikasi kondisi server dan koneksi database.


🗒️ Aturan Bisnis yang Dites (Automated Testing)
Berikut adalah aturan bisnis yang harus divalidasi melalui automated testing:
Validasi Berkas CV
Sistem hanya menerima file CV berformat PDF dengan ukuran maksimal 2 MB.
Anti-Double Apply
Pelamar tidak diperbolehkan mengirimkan lamaran lebih dari satu kali pada lowongan pekerjaan yang sama.
Kadaluarsa Lowongan
Lowongan yang telah melewati batas tanggal berlaku secara otomatis ditutup dan tidak dapat menerima lamaran baru.
Validasi Alur Status
Perubahan status lamaran harus mengikuti alur transisi yang valid, yaitu DIKIRIM → DITINJAU → DITERIMA atau DITOLAK.

📌 Volume Upload Persisten
File CV dalam format PDF disimpan menggunakan Docker Named Volume bernama cv_data_volume.
Penggunaan named volume bertujuan agar file CV yang telah diunggah tetap tersimpan dengan aman dan dapat diakses kembali meskipun terjadi proses restart, penghapusan, maupun re-deploy container.
Dengan demikian, data file CV tidak hilang ketika container aplikasi dibuat ulang.

💻 Cara Menjalankan di Komputer Lokal
- Menjalankan Automated Test
Sebelum menjalankan aplikasi, lakukan pengujian untuk memastikan seluruh fitur dan aturan bisnis berjalan sesuai kebutuhan.
Sesuaikan perintah berikut dengan framework backend yang digunakan.

Node.js (Express.js):
npm install
npm test

Laravel:
composer install
php artisan test

Python (FastAPI):
pip install -r requirements.txt
pytest

Spring Boot:
mvn test

Pastikan seluruh automated test berhasil sebelum melanjutkan ke tahap deployment.
