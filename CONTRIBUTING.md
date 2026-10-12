# Contributing

## Workflow
1. Buat branch dari `main`: `feature/<nama>`, `fix/<nama>`, `docs/<nama>`
2. Commit kecil dengan pesan konvensional: `feat:`, `fix:`, `test:`, `docs:`, `ci:`, `chore:`
3. Jalankan `make lint test` sebelum push
4. Buka Pull Request memakai template; CI harus hijau sebelum merge
5. Merge ke `main` (squash); rilis diberi tag `vX.Y.Z`

## Aturan
- Setiap perubahan perilaku wajib punya test
- Jangan commit secret; konfigurasi lewat environment variable
- Update README/docs bila mengubah cara pakai
- Kode hasil AI harus dibaca, dijalankan, dan di-test sebelum di-commit
