import requests
import feedparser
import time
import os
import sys

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

sumber = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.reuters.com/breakingviews/rss",
    "https://foreignpolicy.com/feed/"
]

prompt_analis = """Kamu analis geopolitik profesional. Buat laporan analisis sentimen dari berita berikut. Format:

1. Ringkasan Eksekutif: Apa inti peristiwa dan mengapa penting bagi AS?
2. Sentimen Negara: Skor sentimen (Positif/Netral/Negatif) untuk 1-2 negara terlibat.
3. Analisis Dampak: Potensi dampak ke stabilitas kawasan atau kepentingan AS.
4. Pandangan Analis: Simulasikan sudut pandang analis intelijen think-tank.

Berita:
"""

def rangkum_ai(teks_berita):
    prompt_lengkap = prompt_analis + teks_berita

    daftar_model_gemini = ["gemini-3.8-flash"]
    for model in daftar_model_gemini:
        for percobaan in range(3):
            print(f"[Gemini] Mencoba {model}, percobaan ke-{percobaan+1}...")
            url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + GEMINI_KEY
            data = {"contents": [{"parts": [{"text": prompt_lengkap}]}]}
            try:
                r = requests.post(url, json=data, timeout=30)
                hasil = r.json()
                if "candidates" in hasil:
                    print("[Gemini] BERHASIL!")
                    return hasil["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    pesan_error = hasil.get("error", {}).get("message", "Unknown error")
                    print(f"[Gemini] Gagal: {pesan_error}")
                    break
            except Exception as e:
                print(f"[Gemini] Error: {e}, tunggu 5 detik...")
                time.sleep(5)

    print("--- Gemini gagal, beralih ke Groq ---")
    daftar_model_groq = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    for model in daftar_model_groq:
        for percobaan in range(3):
            print(f"[Groq] Mencoba {model}, percobaan ke-{percobaan+1}...")
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": "Bearer " + GROQ_KEY,
                "Content-Type": "application/json"
            }
            data = {"model": model, "messages": [{"role": "user", "content": prompt_lengkap}]}
            try:
                r = requests.post(url, headers=headers, json=data, timeout=30)
                hasil = r.json()
                if "choices" in hasil:
                    print("[Groq] BERHASIL!")
                    return hasil["choices"][0]["message"]["content"]
                else:
                    pesan_error = hasil.get("error", {}).get("message", "Unknown error")
                    print(f"[Groq] Gagal: {pesan_error}")
                    break
            except Exception as e:
                print(f"[Groq] Error: {e}, tunggu 5 detik...")
                time.sleep(5)

    return "Semua penyedia AI sedang error. Coba lagi nanti."

teks_gabung = ""
for url_rss in sumber:
    try:
        berita = feedparser.parse(url_rss)
        for item in berita.entries[:3]:
            teks_gabung = teks_gabung + "- " + item.title + "\n"
    except:
        pass

if len(teks_gabung) < 100:
    print("Berita terlalu sedikit, skip.")
    sys.exit()

print("Sedang merangkum...")
hasil = rangkum_ai(teks_gabung)
print("HASIL:", hasil)

pesan = "📰 *ANALIS GEOPOLITIK*\n\n" + hasil
url_tg = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"

max_panjang = 4000
potongan = []
while len(pesan) > max_panjang:
    potong_di = pesan.rfind("\n", 0, max_panjang)
    if potong_di == -1:
        potong_di = max_panjang
    potongan.append(pesan[:potong_di])
    pesan = pesan[potong_di:].lstrip()
potongan.append(pesan)

for i, bagian in enumerate(potongan):
    print(f"Mengirim bagian {i+1} dari {len(potongan)}...")
    r = requests.post(url_tg, data={
        "chat_id": CHAT_ID,
        "text": bagian,
        "parse_mode": "Markdown"
    })
    if r.status_code == 200:
        print(f"Bagian {i+1} terkirim")
    else:
        print(f"Bagian {i+1} GAGAL: {r.json()}")

print("Selesai! Cek Telegram.")
