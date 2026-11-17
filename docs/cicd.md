# CI/CD Jenkins KerjaYuk

`Jenkinsfile` ada di root repo dan menggunakan Declarative Pipeline. Tahap otomatisnya meliputi checkout, pemasangan dependensi pengembangan, lint Ruff, kompilasi Python, pytest dan laporan JUnit, pembuatan PDF laporan, serta build image API dan Nginx. Tahap deploy Compose hanya berjalan untuk branch `main` ketika parameter `DEPLOY` diaktifkan.

## Persiapan Jenkins

Jalankan Jenkins pada mesin/agent Linux. Image lokal proyek di [`jenkins/Dockerfile`](../jenkins/Dockerfile) menambahkan Python 3.13, Docker CLI/Compose, dan plugin Pipeline, GitHub Branch Source, Stage View, serta JUnit ke image resmi Jenkins. Script `jenkins/init.groovy.d/create-kerjayuk-multibranch.groovy` membuat job `KerjaYuk` saat Jenkins pertama kali memakai volume data. Job membaca public repo tanpa token dan menemukan branch serta pull request yang memiliki Jenkinsfile. Build image tersebut:

```sh
docker build -f jenkins/Dockerfile -t kerjayuk-jenkins:local .
```

Profil `ci` menjalankan Jenkins dengan volume data yang sudah ada serta Docker socket untuk stage build image. Di Docker Desktop Windows, grup socket adalah `0`; di Linux, set `DOCKER_GID` ke GID socket Docker. Container tetap berjalan di `127.0.0.1:8080`:

```sh
docker compose --profile ci up -d --build jenkins
```

Jenkins job memerlukan Docker daemon untuk stage `docker compose build`. Akses socket memberi Jenkins kendali luas atas Docker host. Gunakan hanya untuk repo dan pipeline yang dipercaya; periksa Jenkinsfile sebelum menerima PR yang tidak dipercaya.

1. Pilih **New Item → Multibranch Pipeline**.
2. Tambahkan **GitHub Branch Source**, set owner `PasyaAyy`, dan pilih repo `KerjaYuk`.
3. Untuk repo private, simpan credential akses GitHub dengan izin minimum di **Manage Jenkins → Credentials**, lalu pilih credential itu di Branch Source. Repo publik bisa dipindai tanpa token yang ditaruh di source code.
4. Aktifkan discovery untuk branch dan pull request. Jenkins Multibranch akan mencari `Jenkinsfile` dari branch/PR yang ditemukan dan membuat job pipeline per branch.
5. Di **Scan Multibranch Pipeline Triggers**, aktifkan pemindaian berkala agar branch baru tetap ditemukan jika webhook belum siap.

Dokumentasi Jenkins menjelaskan setup Multibranch dan penemuan branch/PR di [Branches and Pull Requests](https://www.jenkins.io/doc/book/pipeline/multibranch/) dan [Pipeline as Code](https://www.jenkins.io/doc/book/pipeline/pipeline-as-code/).

## GitHub Webhook melalui Ngrok

Jenkins harus punya URL HTTPS yang dapat dijangkau GitHub. Untuk demo di komputer lokal, Ngrok dapat meneruskan port Jenkins, misalnya `ngrok http 8080`; gunakan hostname HTTPS yang diberikan Ngrok sebagai URL Jenkins eksternal. Di GitHub repo buka **Settings → Webhooks → Add webhook**, masukkan endpoint webhook yang ditampilkan plugin Jenkins. Endpoint umum GitHub plugin berbentuk `https://HOST-JENKINS/github-webhook/`; cek endpoint aktual pada konfigurasi Jenkins sebelum mendaftarkan. Pilih payload JSON dan event push/pull request yang sesuai sumber branch Jenkins.

Simpan Ngrok authtoken dan GitHub token sebagai credentials/environment secrets lokal atau di Jenkins Credentials. Jangan taruh token, password, atau URL bertoken di `Jenkinsfile`, `.env.example`, log, atau commit. Batasi akses Jenkins dengan akun dan izin yang sesuai sebelum mengeksposnya melalui tunnel.

## Build dan deploy

- Setiap branch/PR menjalankan lint, kompilasi, tes, pembuatan laporan, dan build kedua image.
- Tes menggunakan SQLite sementara; tahap test tidak memerlukan database production.
- Deploy Compose tidak otomatis. Untuk demo, jalankan build branch `main` dan aktifkan parameter `DEPLOY` setelah memeriksa hasil tes. Service memakai named volume untuk database dan CV.
- Deploy memerlukan agent dengan Docker daemon yang menjalankan stack tersebut serta file environment yang disiapkan dengan secret lokal. Jangan gunakan password contoh untuk deployment yang dapat diakses orang lain.
- Tahap pipeline telah disiapkan, tetapi webhook Jenkins belum diaktifkan pada repo ini karena belum ada instance Jenkins/credential terhubung.
