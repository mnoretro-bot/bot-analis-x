import requests
import feedparser

import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

sumber = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.reuters.com/breakingviews/rss",
    "https://foreignpolicy.com/feed/"
]

import time

def rangkum_ai(teks_berita):
    daftar_model = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]

    for model in daftar_model:
        for percobaan in range(3):
            print(f"Mencoba model {model}, percobaan ke-{percobaan+1}...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=" + GEMINI_KEY
            data = {
                "contents": [{
                    "parts": [{"text": "Kamu analis geopolitik profesional. Buat laporan analisis sentimen dari berita berikut. Format:\n\n1. Ringkasan Eksekutif: Apa inti peristiwa dan mengapa penting bagi AS?\n2. Sentimen Negara: Skor sentimen (Positif/Netral/Negatif) untuk 1-2 negara terlibat.\n3. Analisis Dampak: Potensi dampak ke stabilitas kawasan atau kepentingan AS.\n4. Pandangan Analis: Simulasikan sudut pandang analis intelijen think-tank.\n\nBerita:\n" + teks_berita}]
                }]
            }
            try:
                r = requests.post(url, json=data, timeout=30)
                hasil = r.json()
                print("DEBUG:", hasil)
                if "candidates" in hasil:
                    return hasil["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"Model {model} gagal, coba model lain...")
                    break
            except Exception as e:
                print(f"Error: {e}, tunggu 10 detik...")
                time.sleep(10)

    return "Semua model Gemini sedang error. Coba lagi nanti."
teks_gabung = ""
for url_rss in sumber:
    try:
        berita = feedparser.parse(url_rss)
        for item in berita.entries[:3]:
            teks_gabung = teks_gabung + "- " + item.title + "\n"
    except:
        pass

print("Sedang merangkum...")
hasil = rangkum_ai(teks_gabung)
print("HASIL:", hasil)

pesan = "📰 ANALIS GEOPOLITIK\n\n" + hasil
url_tg = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
requests.post(url_tg, data={"chat_id": CHAT_ID, "text": pesan})

print("Selesai! Cek Telegram.")
