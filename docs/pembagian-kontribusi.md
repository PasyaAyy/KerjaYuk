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

Implementasi yang sekarang ada di komputer pemilik belum muncul di GitHub. Pemilik perlu meninjau dan menerbitkan baseline proyek dari akunnya sendiri ke `main` terlebih dahulu. Setelah itu, anggota clone atau pull `main` terbaru dan mengerjakan bagian miliknya. Jangan mengubah identitas commit baseline menjadi nama anggota.

Anggota bekerja berurutan supaya setiap branch mulai dari `main` terbaru dan tidak saling menimpa. Pemilik repo menggabungkan satu PR, lalu anggota berikutnya memperbarui `main` sebelum membuat branch. Checkout ini saat ini berisi banyak file proyek yang belum di-commit; jangan langsung menamai seluruh perubahan tersebut sebagai kontribusi anggota. Setiap orang perlu meninjau area tugasnya dan membuat perubahan yang memang ia kerjakan sebelum commit.

```sh
git switch main
git pull origin main
git switch -c feature/backend-brilliant
# kerjakan, tinjau, dan jalankan verifikasi bagian yang ditugaskan
git add -p
git commit -m "feat(api): complete KerjaYuk backend"
git push -u origin feature/backend-brilliant
```

Di GitHub, buka **Pull requests → New pull request**, pilih `main` sebagai base dan branch anggota sebagai compare, isi ringkasan serta bukti verifikasi, lalu buat PR. Minta review pemilik/Tech Lead. Setelah PR diterima dan digabung, anggota berikutnya memperbarui `main` dan mengulangi alur yang sama.

Branch yang disarankan:

1. `feature/backend-brilliant`
2. `feature/devops-garda`
3. `feature/container-naufal`
4. `feature/qa-docs-pasya`

Gunakan daftar path berikut sebagai panduan area. Stage hanya file atau hunks yang benar-benar dikerjakan anggota setelah baseline tersedia; hindari `git add .` dan stage seluruh direktori tanpa meninjau isinya. Periksa `git diff --cached` sebelum commit.

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

## Status checkout saat panduan dibuat

Checkout lokal saat ini memiliki implementasi tambahan yang belum di-commit dan belum dipush; `origin/main` masih menunjuk commit `9cc10a6`. Perubahan lokal itu tidak dapat diambil anggota melalui GitHub sampai diterbitkan oleh pemilik checkout. Jangan mengganti author commit menjadi anggota lain hanya untuk memunculkan nama mereka. Berikan tiap orang tugas implementasi, review, atau perbaikan nyata pada area kepemilikannya, lalu biarkan mereka membuat commit sendiri.

Di komputer ini GitHub CLI (`gh`) belum tersedia, jadi undangan kolaborator dan pembuatan pull request dilakukan oleh pemilik melalui situs GitHub. Repo juga belum tersambung ke instance Jenkins; `Jenkinsfile` baru mendefinisikan pipeline.
