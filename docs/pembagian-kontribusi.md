# Pembagian Kerja dan Kontribusi GitHub

Panduan ini membagi pekerjaan KerjaYuk berdasarkan peran tim. Setiap anggota membuat perubahan atau review nyata pada bagian yang ditugaskan, lalu mengirim pull request dengan akun GitHub sendiri.

## Pembagian per orang

| Anggota | Peran | Area kepemilikan | Hasil kerja |
| --- | --- | --- | --- |
| Muhammad Brilliant Agung Wicaksono (`102062400126`) | Tech Lead / Backend | Struktur project, `app/`, `migrations/`, `alembic.ini`, `requirements.txt` | Endpoint dan aturan bisnis, migrasi serta seeder, fitur inti, dan pull request backend yang di-merge. |
| Ahmad Nurtajalla Garda Islam (`102062400012`) | DevOps Engineer | `Jenkinsfile`, `docs/cicd.md` | Jenkins job/multibranch, webhook dan Ngrok, credentials, pipeline; bukti konfigurasi job, Stage View, dan console log. Secret disimpan di Jenkins, bukan Git. |
| Muhammad Naufal Syamdany (`102062400100`) | Container Engineer | `Dockerfile`, `compose.yaml`, `.env.example`, `nginx/`, `.dockerignore` | Build container, health checks, environment dan service; bukti konfigurasi file, `docker compose config`, dan output `docker compose ps`. |
| Pasya Ayu Rastiti (`102062400004`) | QA Engineer & Tech Writer | `tests/`, `requirements-dev.txt`, `tools/`, `docs/laporan.*`, `docs/portal-preview.png`, `README.md`, diagram pipeline, `web/`, `KerjaYuk.figcraft` | Unit/feature tests, skenario pipeline gagal lalu pulih, README, diagram alur pipeline, laporan PDF, bukti test dan screenshot build merah lalu hijau; koordinasi UI. |

### Bagian antarmuka web

Frontend berada di `web/` dan rancangan FigCraft di `KerjaYuk.figcraft`. Karena tidak ada peran frontend tersendiri, Pasya mengoordinasikan UI sambil menjalankan tanggung jawab QA dan Tech Writer. Brilliant menetapkan kontrak API dan meninjau integrasinya. Perubahan yang dilaporkan sebagai karya anggota harus benar-benar ditulis atau ditinjau oleh anggota tersebut.

## Siapkan akses repo

Pemilik repo `PasyaAyy/KerjaYuk` membuka **Settings → Collaborators → Add people**, mencari username GitHub tiap anggota, lalu mengirim undangan. Setiap anggota perlu menerima undangan sebelum push branch. Jika akses kolaborator tidak dipakai, anggota dapat fork repo lalu mengirim pull request dari fork masing-masing.

Setiap anggota memastikan email commit terverifikasi atau alamat `noreply` milik akun GitHub sendiri. Atur identitas lokal di clone KerjaYuk, bukan dengan menyalin identitas orang lain:

```sh
git config user.name "Nama GitHub Anda"
git config user.email "Email-terverifikasi-atau-noreply-GitHub-Anda"
git config --get user.name
git config --get user.email
```

Email `noreply` dapat dilihat di **GitHub Settings → Emails**. Alamat commit yang tidak terkait ke akun GitHub tidak otomatis ditampilkan sebagai kontribusi akun tersebut.

## Terbitkan baseline, lalu kirim pekerjaan satu per satu

Baseline proyek sudah dipush ke branch `chore/kerjayuk-project-baseline` dan tersedia sebagai PR #1 ke `main`. Saat status ini dicatat, PR masih terbuka; `main` belum berisi baseline tersebut. Jangan mengganti author commit atau mengatasnamakan perubahan anggota lain. Setiap anggota harus membuat perubahan nyata di area tugasnya dan commit dengan akun GitHub sendiri.

Langkah berikutnya adalah meminta pemilik repo `PasyaAyy` meninjau dan menggabungkan PR #1. Akun `garda05` memiliki akses push tetapi tidak memiliki izin admin/merge pada repo ini. Setelah baseline masuk ke `main`, anggota bekerja berurutan dari `main` terbaru dan mengirim PR ke `main`.

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/backend-brilliant
# kerjakan dan tinjau perubahan milik sendiri pada area tugas
git add -p
git commit -m "feat(api): improve KerjaYuk backend"
git push -u origin feature/backend-brilliant
```

Di GitHub, buka **Pull requests → New pull request**, pilih `main` sebagai base dan branch anggota sebagai compare, isi ringkasan serta bukti verifikasi, lalu buat PR. Minta review pemilik/Tech Lead. Setelah PR diterima dan digabung, anggota berikutnya memperbarui `main` dan mengulangi alur yang sama.

Branch yang disarankan:

1. `feature/backend-brilliant`
2. `feature/devops-garda`
3. `feature/container-naufal`
4. `feature/qa-docs-pasya`

Gunakan daftar path sebagai panduan area, bukan bukti kepengarangan atas perubahan baseline yang sudah ada. Stage hanya file atau hunk yang benar-benar dikerjakan anggota; hindari `git add .` dan tinjau `git diff --cached` sebelum commit.

```sh
# Brilliant: pilih perubahan backend miliknya
git add -p

# Garda: pilih perubahan Jenkins/CI miliknya
git add -p

# Naufal: pilih perubahan container miliknya
git add -p

# Pasya: pilih perubahan QA, dokumentasi, atau UI miliknya
git add -p
```

Sesuaikan `git add` agar hanya mencakup file yang benar-benar diubah oleh anggota itu. Buat pull request ke `PasyaAyy/KerjaYuk:main`, tulis ringkasan dan bukti tes, lalu tunggu review sebelum merge. Jika menggunakan fork, tambahkan remote upstream satu kali:

```sh
git remote add upstream https://github.com/PasyaAyy/KerjaYuk.git
git fetch upstream
git switch -c feature/backend-brilliant upstream/main
git push -u origin feature/backend-brilliant
```

Sesudah PR digabung, anggota berikutnya menjalankan `git switch main` lalu `git pull origin main` (atau `git fetch upstream` dan membuat branch dari `upstream/main` jika menggunakan fork).

## Supaya tampil sebagai kontributor GitHub

- Commit harus dibuat dengan identitas dan email GitHub milik orang yang mengerjakan perubahan.
- Pull request harus digabung ke branch default repo (`main`). Push ke branch fitur saja belum memasukkan commit ke riwayat default branch.
- Pemilik repo sebaiknya memakai **Create a merge commit** atau **Rebase and merge** supaya commit asli anggota tetap berada di riwayat `main`. Squash merge menggabungkan PR menjadi satu commit dan menghilangkan informasi commit individual.
- Sesudah GitHub memproses riwayat, cek **Insights → Contributors**. Grafik menghitung commit di branch default, perlu email author yang terhubung dengan akun, dan dapat memerlukan sampai 24 jam untuk diperbarui.

Lihat [panduan GitHub tentang grafik kontributor repo](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-a-projects-contributors) dan [atribusi commit](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors) jika nama kontributor belum terhubung ke akun.

## Status penyelesaian dan bukti

Status terakhir diperiksa pada 17 November 2026:

- PR #1 (`chore/kerjayuk-project-baseline` ke `main`) masih terbuka; baseline belum masuk ke `main` dan pemilik repo perlu meninjau serta menggabungkannya.
- Grafik kontributor branch default saat ini menampilkan `PasyaAyy` dan `garda05`. Anggota lain belum tercatat di riwayat default. Mereka harus membuat commit sendiri setelah baseline masuk ke `main`; jangan membuat commit atas nama mereka.
- Container aplikasi (`nginx`, `api`, `db`) aktif dan health check Docker berstatus sehat. Jenkins lokal menjawab HTTP 200 pada `/login`.
- GitHub pernah menerima webhook `ping` dengan HTTP 200. Ping hanya memeriksa endpoint; belum ada bukti build Jenkins terbaru yang dipicu oleh event `push` atau `pull_request`.
- Screenshot Stage View, console log, hasil `docker compose ps`, serta skenario build gagal lalu pulih tetap harus diambil dari pelaksanaan anggota. Jangan menuliskan bukti seolah-olah sudah tersedia.

Pemilik repo mengelola undangan kolaborator, webhook, dan merge karena akses `garda05` bukan admin. Undangan dan PR dapat ditangani melalui situs GitHub; GitHub CLI tidak wajib.
