# 👻 TELEGHOST – Spyware Telegram Edition

TELEGHOST adalah spyware ringan berbasis Python yang dikendalikan sepenuhnya melalui bot Telegram.  
Alat ini dibuat untuk tujuan **edukasi dan pengujian keamanan** di perangkat sendiri.

---

## 🔍 Apa Itu TELEGHOST?

TELEGHOST bekerja seperti hantu digital.  
Lo kirim perintah lewat chat Telegram, dan target (HP/PC) menjalankannya tanpa curiga.  
Semua hasil dikirim balik ke Telegram lo secara real-time.

**Keunggulan utama:**
- Tanpa dashboard – semua kontrol via Telegram.
- Multi-platform – Windows, Linux, Android (Termux).
- Real-time – hasil langsung masuk ke chat lo.
- Stealth – berjalan di background tanpa ketahuan.
- Auto-start – otomatis jalan saat boot.

---

## 🧩 Fitur Lengkap

| Fitur | Fungsi |
|-------|--------|
| Screenshot | Ambil gambar layar target |
| Screen Recorder | Rekam layar target (video) |
| Keylogger | Rekam semua ketikan target |
| Rekam Mic | Rekam suara dari mikrofon |
| Kamera | Ambil foto & video dari kamera |
| GPS / Lokasi | Dapatkan lokasi target (IP geolocation) |
| Remote Command | Jalankan perintah sistem |
| Upload File | Ambil file dari target |
| Download File | Kirim file ke target |
| Notifikasi Otomatis | Alert tanpa perintah (aplikasi dibuka, kata sensitif, gerakan kamera, suara keras) |
| Auto-Start | Jalan otomatis saat boot |
| Stealth Mode | Berjalan di background tanpa ketahuan |

---

## ⚙️ Cara Kerja

Target menjalankan TELEGHOST → TELEGHOST terhubung ke bot Telegram → Lo kirim perintah ke bot → Bot meneruskan ke TELEGHOST → TELEGHOST menjalankan perintah → Hasil dikirim balik ke bot → Lo lihat hasil di Telegram.

---

## 🔧 Persiapan Awal

1. Buat bot Telegram melalui @BotFather, simpan **TOKEN**.
2. Kirim pesan ke bot, lalu akses `https://api.telegram.org/bot<TOKEN>/getUpdates` untuk mendapatkan **CHAT_ID**.

---

## 📦 Dependensi

TELEGHOST membutuhkan library Python:
- telebot
- pyautogui
- opencv-python
- pillow
- numpy
- pynput
- pyaudio
- psutil
- requests

Install dengan:
```bash
pip install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
```

---

## 🚀 Cara Jalankan

1. Edit file `teleghost.py`, ganti `BOT_TOKEN` dan `CHAT_ID` dengan punya lo.
2. Jalankan di target:
   - Windows: `python teleghost.py`
   - Linux: `python3 teleghost.py`
   - Termux: `python teleghost.py &`

---

## 📋 Daftar Perintah Telegram

| Perintah | Fungsi |
|----------|--------|
| `/screenshot` | Ambil layar |
| `/screenrec [detik]` | Rekam layar (default 10s) |
| `/keylog_start` | Mulai keylogger |
| `/keylog_stop` | Hentikan & kirim hasil |
| `/mic [detik]` | Rekam mic (default 10s) |
| `/cam_photo` | Foto dari kamera |
| `/cam_video [detik]` | Video dari kamera |
| `/gps` | Kirim lokasi |
| `/cmd [perintah]` | Jalankan perintah sistem |
| `/upload [path]` | Upload file dari target |
| `/download [url] [path]` | Download file ke target |
| `/status` | Cek status TELEGHOST |

---

## 🔔 Notifikasi Otomatis

TELEGHOST akan mengirim alert ke Telegram jika:
- Target membuka aplikasi tertentu (Chrome, WhatsApp, Telegram, dll).
- Target mengetik kata sensitif (password, login, admin, pin, otp).
- Screenshot periodik tiap 5 menit.
- Lokasi GPS berubah lebih dari 500 meter.
- Kamera mendeteksi gerakan.
- Mikrofon menangkap suara keras.

---

## 🖥️ Compile ke .exe (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole teleghost.py
```
Hasil: `dist/teleghost.exe`

---

## 📱 Install di Android (Termux)

```bash
pkg update && pkg install python termux-api -y
pip install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
python teleghost.py &
```

---

## 🐧 Install di Linux

```bash
sudo apt update
sudo apt install python3 python3-pip portaudio19-dev -y
pip3 install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
python3 teleghost.py &
```

Auto-start:
```bash
crontab -e
@reboot python3 /path/to/teleghost.py
```

---

## 🛑 Hentikan TELEGHOST

- Windows: `taskkill /F /IM python.exe`
- Linux/Termux: `pkill -f teleghost.py`

---

## ⚙️ Customization

| Yang Bisa Diubah | Lokasi di Kode |
|------------------|----------------|
| Token & Chat ID | `BOT_TOKEN` & `CHAT_ID` |
| Interval Screenshot | `screenshot_interval = 300` |
| Kata Sensitif | `sensitive_words = [...]` |
| Threshold Suara | `if rms > 1000:` |
| Jarak GPS | `if distance > 500:` |

---

## ❓ Troubleshooting & FAQ

**Q: TELEGHOST gak kirim data ke Telegram?**  
A: Cek `BOT_TOKEN` dan `CHAT_ID`, pastikan koneksi internet target aktif.

**Q: Keylogger gak nangkap huruf?**  
A: Pastikan `pynput` terinstall. Di Android hanya berfungsi di Termux.

**Q: Rekam layar gagal di Android?**  
A: Butuh izin "Screen Recording" — target harus klik Allow.

**Q: Error pyaudio di Linux?**  
A: Install `portaudio19-dev`, lalu `pip install pyaudio --force-reinstall`.

**Q: Bisa dipakai di iPhone?**  
A: Tidak. Hanya Windows, Linux, dan Android (Termux).

**Q: Antivirus mendeteksi TELEGHOST?**  
A: Gunakan crypter atau obfuscation (PyArmor, UPX).

**Q: Berapa ukuran file TELEGHOST?**  
A: Python ~20-30 KB. .exe ~5-10 MB.

**Q: Bisa untuk banyak target?**  
A: Satu bot untuk satu target. Buat bot baru untuk target lain.

**Q: Data tersimpan di server Telegram?**  
A: Ya. Hindari kirim data sangat sensitif.

---
