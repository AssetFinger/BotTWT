# 🤖 Twitter/X Automation Bot (Playwright)

Bot CLI berbasis Python menggunakan **Playwright** untuk mengotomatisasi beberapa aktivitas di Twitter/X secara aman menggunakan file `cookie.json`. 

## 🚀 Fitur Utama
* **Menu 1 & 2:** Manajemen penyimpanan & pengecekan daftar cookie akun.
* **Menu 3 (Follow Target):** Fitur follow massal atau manual (pilih akun tertentu) dilengkapi dengan jeda waktu acak (*random delay*) agar aman dari *banned*.
* **Menu 4 (Komentar Tweet):** Fitur otomatis komentar ke target tweet dengan opsi menggunakan link baru atau link yang tersimpan. Dilengkapi fitur *auto-scroll* jika kolom komentar belum termuat.
* **Menu 5 (Cek Status Akun):** Melakukan pengecekan kesehatan akun secara massal untuk mendeteksi apakah cookie kedaluwarsa (*expired*), akun ditangguhkan (*suspended*), atau terkunci (*locked*).

---

## 🛠️ Langkah Instalasi

Ikuti langkah-langkah di bawah ini untuk menyiapkan bot di komputer Anda (sangat ramah untuk pengguna Warnet/VPS):

1. Pastikan Python Sudah Terinstal
Buka Command Prompt (CMD) atau Terminal, lalu cek versi Python Anda:
```bash
python --version
```

2. Instal Dependensi & Library Utama
Jalankan perintah berikut di CMD untuk menginstal pustaka Playwright:
```bash
pip install playwright
```

3. Instal Browser Chromium untuk Bot
Unduh browser khusus yang akan digunakan oleh Playwright untuk menjalankan otomasi:

```bash
playwright install chromium
```

4. Beraksi
```bash
python bot_twitter.py
```
