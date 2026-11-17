# CI/CD Jenkins KerjaYuk

`Jenkinsfile` ada di root repo dan menggunakan Declarative Pipeline. Tahap otomatisnya meliputi checkout, pemasangan dependensi pengembangan, lint Ruff, kompilasi Python, pytest dan laporan JUnit, pembuatan PDF laporan, serta build image API dan Nginx. Tahap deploy Compose hanya berjalan untuk branch `main` ketika parameter `DEPLOY` diaktifkan.

## Persiapan Jenkins

Jalankan Jenkins pada Docker Desktop dengan Linux containers atau Docker Engine. Image lokal proyek di [`jenkins/Dockerfile`](../jenkins/Dockerfile) menambahkan Python 3.13, Docker CLI/Compose, serta plugin Pipeline, GitHub, GitHub Branch Source, Stage View, dan JUnit. Script `jenkins/init.groovy.d/create-kerjayuk-multibranch.groovy` membuat job `KerjaYuk` saat Jenkins pertama kali memakai volume data. Job menemukan branch serta pull request yang memiliki Jenkinsfile. Untuk pemindaian cepat dan status build GitHub, tambahkan fine-grained token yang dibatasi ke repo `KerjaYuk` sebagai credential Jenkins; jangan simpan token dalam source code. Build image Jenkins:

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
3. Buat fine-grained token yang dibatasi ke `KerjaYuk` dengan izin metadata dan pull requests read-only; simpan sebagai credential Jenkins dan pilih sebagai Scan Credential. Tambahkan izin commit status bila Jenkins perlu mengirim status build kembali ke GitHub.
4. Aktifkan discovery untuk branch dan pull request. Jenkins Multibranch akan mencari `Jenkinsfile` dari branch/PR yang ditemukan dan membuat job pipeline per branch.
5. Gunakan webhook untuk pemindaian segera; pilih pemindaian berkala hanya sebagai fallback.

Dokumentasi Jenkins menjelaskan setup Multibranch dan penemuan branch/PR di [Branches and Pull Requests](https://www.jenkins.io/doc/book/pipeline/multibranch/) dan [Pipeline as Code](https://www.jenkins.io/doc/book/pipeline/pipeline-as-code/).

## GitHub Webhook melalui Ngrok

Ngrok memerlukan akun dan authtoken. Setelah authtoken tersedia, simpan di konfigurasi lokal Ngrok lalu jalankan tunnel:

```powershell
ngrok config add-authtoken <AUTHTOKEN_DARI_DASHBOARD_NGROK>
ngrok http 8080
```

Salin alamat HTTPS yang ditampilkan Ngrok. Pastikan akun Jenkins memakai password yang kuat sebelum tunnel berjalan; Jenkins hanya terikat ke `127.0.0.1:8080` pada host, sedangkan tunnel membuat URL publik yang meneruskan request ke Jenkins.

> Pembuatan atau perubahan webhook repository memerlukan akses owner/admin; akses `push` saja tidak cukup. Jika URL Ngrok berubah, perbarui Payload URL webhook dan Jenkins URL memakai alamat HTTPS yang sedang aktif.

Saat Jenkins mulai, script bootstrap membuat credential **Secret text** bernama `kerjayuk-github-webhook-secret`, memasangnya untuk validasi signature SHA-256, lalu menyimpan salinannya di volume data Jenkins. Salin nilai itu ke AppData lokal untuk dimasukkan pada secret webhook GitHub:

```powershell
$secretDir = Join-Path $env:LOCALAPPDATA 'KerjaYuk'
New-Item -ItemType Directory -Force $secretDir | Out-Null
docker cp kerjayuk-jenkins:/var/jenkins_home/secrets/kerjayuk-github-webhook-secret.txt (Join-Path $secretDir 'github-webhook-secret.txt')
```

Atur Jenkins URL ke alamat HTTPS Ngrok agar tautan build mengarah ke alamat yang bisa dijangkau GitHub.

Di GitHub buka **Settings → Webhooks → Add webhook**, lalu atur:

- Payload URL: `https://<HOST_NGROK>/github-webhook/`
- Content type: `application/json`
- Secret: nilai yang sama dengan credential webhook Jenkins
- Events: **Pushes** dan **Pull requests**

Klik **Add webhook**, lalu gunakan **Recent Deliveries → Redeliver** untuk memeriksa respons. GitHub Branch Source memproses event dari endpoint `/github-webhook/` dan memperbarui indeks branch/PR. Untuk mengurangi jeda API anonim, simpan token GitHub fine-grained terbatas untuk repo `KerjaYuk` sebagai Jenkins credential dan pilih di konfigurasi sumber GitHub job.

Jangan taruh Ngrok authtoken, GitHub token, webhook secret, atau URL bertoken di `Jenkinsfile`, `.env.example`, log, atau commit. Hentikan tunnel setelah sesi demo bila tidak diperlukan.

## Jenkins permanen di server

### Akses dari perangkat lain tanpa VPS

Ngrok menetapkan satu dev domain gratis untuk akun dan endpoint `ngrok http 8080` menggunakannya otomatis; domain itu tetap sama saat agent dimulai ulang. Jadi browser di perangkat lain dapat memakai URL Ngrok yang sama tanpa memasang Jenkins di perangkat client. Jalankan `scripts/install-local-ci-startup.ps1` sekali di PC host untuk memasang task Windows yang menunggu Docker Desktop, memastikan Jenkins aktif, lalu menjalankan Ngrok di latar belakang. Log startup tersimpan di `%LOCALAPPDATA%\KerjaYuk\local-ci-startup.log`.

PC host harus tetap menyala, terhubung ke internet, dan akun Windows tetap login. Ini membuat Jenkins mudah diakses lintas perangkat, tetapi bukan hosting 24/7 jika PC host mati. Hapus task otomatis dengan `Unregister-ScheduledTask -TaskName 'KerjaYuk Local CI' -Confirm:$false`. Dev domain gratis tetap memiliki batas pemakaian bulanan; lihat [batas Free plan Ngrok](https://ngrok.com/docs/pricing-limits).

### Hosting tanpa bergantung pada PC

Jenkins di komputer lokal hanya tersedia saat komputer dan Docker Desktop aktif. Agar dapat dibuka dari perangkat lain kapan saja, jalankan stack ini pada Linux VPS/server yang selalu aktif dan gunakan domain tetap. Konfigurasi `compose.server.yaml` menambahkan Caddy sebagai reverse proxy HTTPS untuk Jenkins saja; data Caddy, Jenkins, PostgreSQL, serta CV memakai named volume. Port Jenkins `8080` dan aplikasi `8000` hanya terikat ke loopback. Caddy tidak mempublikasikan portal karena endpoint pengelolaannya belum memiliki autentikasi.

Siapkan server Linux dengan Docker Compose, satu domain Jenkins dengan DNS A/AAAA menuju IP server, serta firewall yang membuka port 80/443 dan SSH terbatas untuk admin. Di server, clone repo, salin `.env.example` menjadi `.env`, isi password database yang kuat, salin `.env.server.example` menjadi `.env.server`, lalu ganti `JENKINS_DOMAIN` dengan hostname Jenkins. Jalankan:

```sh
docker volume create kerjayuk_jenkins_home
docker compose -f compose.yaml -f compose.server.yaml --profile ci --profile server up -d --build
```

Caddy memperoleh dan memperbarui sertifikat otomatis setelah DNS mengarah ke server dan port 80/443 dapat dijangkau dari internet. Data sertifikat disimpan di volume `caddy_data`; dokumentasi [Automatic HTTPS Caddy](https://caddyserver.com/docs/automatic-https) menjelaskan syarat DNS dan portnya. Pastikan pengaturan **Jenkins URL** memakai `https://<JENKINS_DOMAIN>/` sesuai domain proxy. Jenkins harus tetap memakai login; jangan membuka port 8080 atau Docker socket ke internet. Portal tetap hanya tersedia di server pada port `8000` yang terikat ke loopback. Publikasikan aplikasi setelah autentikasi serta kontrol akses tersedia.

Compose memakai nama project tetap `kerjayuk`, sehingga deploy dari Jenkinsfile menargetkan stack dan named volume yang sama. Perintah di atas membuat Jenkins home baru; riwayat build dan credential dari Docker volume di laptop tidak ikut berpindah. Pertahankan Jenkins lokal sampai server baru siap, lalu migrasikan volume secara aman hanya jika Anda perlu mempertahankan riwayat/credential tersebut. Server baru membuat webhook secret sendiri. Tambahkan credential GitHub scan di Jenkins, lalu minta owner/admin repo membuat webhook ke `https://<JENKINS_DOMAIN>/github-webhook/` memakai secret dari `/var/jenkins_home/secrets/kerjayuk-github-webhook-secret.txt`. Setelah endpoint permanen terverifikasi, tunnel Ngrok lokal tidak diperlukan lagi. Lindungi named volume dan buat backup berkala; volume menyimpan konfigurasi Jenkins, credential terenkripsi, database, dan file CV.

## Build dan deploy

- Setiap branch/PR menjalankan lint, kompilasi, tes, pembuatan laporan, dan build kedua image.
- Tes menggunakan SQLite sementara; tahap test tidak memerlukan database production.
- Deploy Compose tidak otomatis. Untuk demo, jalankan build branch `main` dan aktifkan parameter `DEPLOY` setelah memeriksa hasil tes. Service memakai named volume untuk database dan CV.
- Deploy memerlukan agent dengan Docker daemon yang menjalankan stack tersebut serta file environment yang disiapkan dengan secret lokal. Jangan gunakan password contoh untuk deployment yang dapat diakses orang lain.
- Sebelum webhook dan pemindaian API terhubung, pipeline tetap dapat dipindai manual dari **Scan Multibranch Pipeline Now**. Jalankan tunnel hanya selama pengujian webhook.
