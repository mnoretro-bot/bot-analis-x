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

def rangkum_ai(teks_berita):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=" + GEMINI_KEY
    data = {
        "contents": [{
            "parts": [{"text": "Kamu analis geopolitik profesional. Buat laporan analisis sentimen dari berita berikut. Format:\n\n1. **Ringkasan Eksekutif:** Apa inti peristiwa & mengapa penting bagi AS?\n2. **Sentimen Negara:** Skor sentimen (Positif/Netral/Negatif) untuk 1-2 negara terlibat.\n3. **Analisis Dampak:** Potensi dampak ke stabilitas kawasan atau kepentingan ekonomi AS.\n4. **Pandangan Analis:** Simulasikan sudut pandang analis intelijen think-tank.\n\nBerita:\n" + teks_berita}]
        }]
    }
    r = requests.post(url, json=data)
    hasil = r.json()
    print("DEBUG:", hasil)
    if "candidates" in hasil:
        return hasil["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return "Error dari API"

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
