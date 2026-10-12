# AI Usage

Dokumen ini menjelaskan secara jujur teknologi yang dipakai serta pembagian peran antara saya dan AI.

## Teknologi

**AI tools**
- Claude (Anthropic) lewat claude.ai

**Aplikasi**
- Python 3.12, FastAPI, Uvicorn, pydantic
- html.parser bawaan Python untuk membaca HTML
- httpx (dipakai TestClient FastAPI)

**Testing dan kualitas kode**
- pytest (47 test), ruff

**Infrastruktur dan workflow**
- Docker dan Docker Compose (image non-root, HEALTHCHECK)
- Git dan GitHub (branch, Pull Request)
- GitHub Actions (lint, test, build image)
- GitHub Container Registry (ghcr.io)
- Swagger UI (/docs) dan diagram Mermaid

## Peran saya

1. **Menentukan arah dan kebutuhan.** Saya menerima brief tes (aplikasi sederhana, AI-assisted, Git/GitHub, Docker, automated test, dokumentasi, tanpa VPS, maksimal 6 jam) dan menerjemahkannya menjadi permintaan kerja kepada AI.
2. **Memilih ide.** Saya memilih ide yang sederhana dan relevan dengan latar belakang saya (SEO dan bahasa), lalu memilih **SEO Page Checker**.
3. **Menyiapkan lingkungan kerja.** Memasang dan menjalankan Docker Desktop, menyiapkan akun dan repository GitHub, serta mengatasi kendala Docker yang belum aktif.
4. **Mengelola Git dan GitHub.** Membuat repository, membuat branch fitur, melakukan commit dan push, serta mengatur izin GitHub Actions dan GHCR.
5. **Menjalankan dan mencoba aplikasi.** Menjalankan aplikasi di localhost:8000 dan membuka dokumentasi Swagger (/docs) yang menampilkan endpoint /health, /rules, dan /analyze.
6. **Menyusun dokumen ini dan memutuskan untuk mengungkapkan penggunaan AI secara terbuka**, sesuai ketentuan tes.

## Peran AI (Claude)

- Menulis draf kode aplikasi (analyzer, API, models, konfigurasi)
- Menulis draf 47 automated test
- Menulis draf dokumentasi (README, ARCHITECTURE, CONTRIBUTING, AGENTS.md)

## Verifikasi
- Aplikasi berjalan di http://localhost:8000/docs dengan endpoint /health, /rules, dan /analyze
- ruff dan pytest dijalankan otomatis oleh GitHub Actions pada setiap Pull Request (lihat tab Actions)
