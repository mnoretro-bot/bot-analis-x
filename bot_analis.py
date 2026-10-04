import requests
import feedparser

import os
                                                           TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")               GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
sumber = [
    "https://www.cnbcindonesia.com/rss",
    "https://www.antaranews.com/rss/terkini.xml"
]

def rangkum_ai(teks_berita):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=" + GEMINI_KEY
    data = {
        "contents": [{
            "parts": [{"text": "Rangkum berita berikut jadi 3 poin penting dalam bahasa Indonesia:\n\n" + teks_berita}]
        }]                                                     }
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
        berita = feedparser.parse(url_rss)                         for item in berita.entries[:3]:
            teks_gabung = teks_gabung + "- " + item.title + "\n"
    except:
        pass

print("Sedang merangkum...")
hasil = rangkum_ai(teks_gabung)
print("HASIL:", hasil)

pesan = "📰 ANALIS BERITA HARI INI\n\n" + hasil
url_tg = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
requests.post(url_tg, data={"chat_id": CHAT_ID, "text": pesan})                                                       
print("Selesai! Cek Telegram.")
