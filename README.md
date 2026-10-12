# SEO Page Checker

![CI](https://github.com/benisobahasa/seo-page-checker/actions/workflows/ci.yml/badge.svg)

Layanan kecil berbasis FastAPI yang menerima **HTML sebuah halaman** dan mengembalikan **laporan SEO on-page**:
skor 0-100, grade A-F, statistik halaman, dan temuan per aturan beserta saran perbaikannya.

Dibuat sebagai layanan yang siap dipakai di production dan mudah dilanjutkan engineer lain.

## Fitur
- `POST /analyze`: analisis HTML, hasilnya skor, grade, statistik, dan 12 temuan
- `GET /rules`: daftar aturan, tingkat keparahan, dan bobot
- `GET /health`: liveness check (dipakai Docker HEALTHCHECK)
- Tidak mengambil halaman dari internet (hanya memproses HTML yang dikirim), sehingga tidak ada risiko SSRF
- Tanpa dependency parsing tambahan (memakai `html.parser` bawaan Python)

## Quick start (Docker)
```bash
docker compose up --build
curl http://localhost:8000/health
```
Dokumentasi API interaktif (Swagger): http://localhost:8000/docs

## Mencoba analisis
Terminal 1 menjalankan server, Terminal 2:
```bash
python3 -c 'import json,sys; print(json.dumps({"html": open(sys.argv[1]).read()}))' examples/bad_page.html \
  | curl -s -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d @-
```
Contoh hasil (temuan dipotong 3 pertama):
```json
{
  "score": 20,
  "grade": "F",
  "passed": 2,
  "failed": 10,
  "stats": {
    "title": "Home",
    "title_length": 4,
    "meta_description_length": 0,
    "h1_count": 2,
    "image_count": 1,
    "images_missing_alt": 1,
    "word_count": 11
  },
  "findings": [
    {
      "rule_id": "title_present",
      "passed": true,
      "severity": "error",
      "message": "Page has a <title>."
    },
    {
      "rule_id": "title_length",
      "passed": false,
      "severity": "warning",
      "message": "Title is 4 characters; aim for 30-60."
    },
    {
      "rule_id": "meta_description_present",
      "passed": false,
      "severity": "error",
      "message": "Missing meta description. Summarize the page in one or two sentences."
    }
  ]
}
```

## Aturan penilaian
Skor = total bobot aturan yang lolos (bobot seluruhnya berjumlah 100).

| Rule id | Severity | Bobot | Yang dicek |
|---|---|---|---|
| `title_present` | error | 15 | Ada `<title>` tidak kosong |
| `title_length` | warning | 5 | Title 30-60 karakter |
| `meta_description_present` | error | 15 | Ada meta description |
| `meta_description_length` | warning | 5 | Meta description 70-160 karakter |
| `single_h1` | error | 15 | Tepat satu `<h1>` |
| `heading_order` | warning | 5 | Level heading tidak melompat (mis. h2 ke h4) |
| `images_alt` | warning | 10 | Semua `<img>` punya atribut `alt` (alt kosong boleh untuk gambar dekoratif) |
| `canonical_present` | info | 5 | Ada `<link rel="canonical">` |
| `lang_attribute` | warning | 5 | `<html>` punya atribut `lang` |
| `viewport_meta` | warning | 5 | Ada meta viewport |
| `word_count` | info | 10 | Minimal 300 kata (script, style, head tidak dihitung) |
| `indexable` | error | 5 | Meta robots tidak berisi `noindex` |

Grade: A (90+), B (75+), C (60+), D (40+), F (di bawah 40).

## Development lokal
```bash
python3 -m venv .venv
source .venv/bin/activate
make install   # pasang dependency
make test      # jalankan automated tests
make lint      # cek gaya kode (ruff)
make run       # server dengan auto-reload di http://localhost:8000
```

## Konfigurasi
| Variabel | Default | Keterangan |
|---|---|---|
| `MAX_HTML_CHARS` | `200000` | Batas panjang field `html` (lebih dari ini ditolak dengan HTTP 422) |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, atau `ERROR` |

Salin `.env.example` ke `.env` untuk pemakaian lokal. Jangan commit `.env`.

## Struktur proyek
```
app/
  config.py      # konfigurasi dari environment variable
  models.py      # skema request/response (pydantic)
  analyzer.py    # parsing HTML + aturan SEO (fungsi murni, tanpa I/O)
  main.py        # lapisan HTTP yang tipis
tests/           # pytest (tanpa jaringan)
examples/        # contoh halaman HTML untuk dicoba
docs/            # dokumentasi arsitektur
.github/         # workflow CI dan template PR
```

## Testing
```bash
make test
```
Test mencakup batas panjang title/description, deteksi heading, alt gambar, noindex, perhitungan kata, input HTML rusak,
batas grade, dan validasi API (422 untuk input salah). Test tidak memanggil jaringan.

## CI/CD
GitHub Actions (`.github/workflows/ci.yml`):
1. Setiap push dan PR: `ruff check` dan `pytest`
2. Build Docker image
3. Saat merge ke `main`: push image ke GitHub Container Registry (`ghcr.io/benisobahasa/seo-page-checker`)

## Deployment
Tidak ada server pada tugas ini, jadi artefak yang dihasilkan adalah image Docker yang bisa dijalankan di mana saja:
```bash
docker run --rm -p 8000:8000 ghcr.io/benisobahasa/seo-page-checker:latest
```
Layanan ini stateless (tanpa database), sehingga mudah diskalakan horizontal di platform container mana pun.

## Roadmap dan keterbatasan
- Hanya menganalisis HTML mentah; halaman yang dirender JavaScript tidak dievaluasi
- Rentang ideal (panjang title, dsb.) adalah heuristik umum, bukan aturan resmi mesin pencari
- Belum ada autentikasi dan rate limiting (perlu sebelum dibuka ke publik)
- Rencana: analisis lewat URL dengan perlindungan SSRF, aturan tambahan (Open Graph, structured data), laporan dalam Bahasa Indonesia

## Untuk engineer berikutnya
- Aturan kontribusi dan workflow Git: [CONTRIBUTING.md](CONTRIBUTING.md)
- Arsitektur dan keputusan teknis: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Panduan untuk AI assistant: [AGENTS.md](AGENTS.md)
- Pemakaian AI di project ini: [AI_USAGE.md](AI_USAGE.md)
- Cara menambah aturan baru: lihat bagian "Menambah aturan" di docs/ARCHITECTURE.md
