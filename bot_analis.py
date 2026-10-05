import requests
import feedparser
import time
import os

# ============ KONFIGURASI ============
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# ============ SUMBER BERITA ============
sumber = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.reuters.com/breakingviews/rss",
    "https://foreignpolicy.com/feed/"
]

# ============ PROMPT ANALIS GEOPOLITIK ============
prompt_analis = """Kamu analis geopolitik profesional. Buat laporan analisis sentimen dari berita berikut. Format:

1. Ringkasan Eksekutif: Apa inti peristiwa dan mengapa penting bagi AS?
2. Sentimen Negara: Skor sentimen (Positif/Netral/Negatif) untuk 1-2 negara terlibat.
3. Analisis Dampak: Potensi dampak ke stabilitas kawasan atau kepentingan AS.
4. Pandangan Analis: Simulasikan sudut pandang analis intelijen think-tank.

Berita:
"""

# ============ FUNGSI RANGKUM AI (Gemini + Groq) ============
def rangkum_ai(teks_berita):
    prompt_lengkap = prompt_analis + teks_berita

    # --- BAGIAN 1: COBA GEMINI DULU ---
    daftar_model_gemini = [
        "gemini-3.8-flash"
    ]

    for model in daftar_model_gemini:
        for percobaan in range(3):
            print(f"[Gemini] Mencoba {model}, percobaan ke-{percobaan+1}...")
            url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + GEMINI_KEY
            data = {
                "contents": [{
                    "parts": [{"text": prompt_lengkap}]
                }]
            }
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

    # --- BAGIAN 2: KALAU GEMINI GAGAL, COBA GROQ ---
    print("--- Gemini gagal semua, beralih ke Groq ---")
    daftar_model_groq = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]

    for model in daftar_model_groq:
        for percobaan in range(3):
            print(f"[Groq] Mencoba {model}, percobaan ke-{percobaan+1}...")
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": "Bearer " + GROQ_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt_lengkap}]
            }
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

    # --- BAGIAN 3: KALAU SEMUA GAGAL ---
    return "Semua penyedia AI sedang error. Coba lagi nanti."

# ============ AMBIL BERITA DARI RSS ============
teks_gabung = ""
for url_rss in sumber:
    try:
        berita = feedparser.parse(url_rss)
        for item in berita.entries[:3]:
            teks_gabung = teks_gabung + "- " + item.title + "\n"
    except:
        pass

# ============ RANGKUM PAKAI AI ============
print("Sedang merangkum...")
hasil = rangkum_ai(teks_gabung)
print("HASIL:", hasil)

# ============ KIRIM KE TELEGRAM (DIPECAH) ============
pesan = "📰 ANALIS GEOPOLITIK\n\n" + hasil
url_tg = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"

# Pecah pesan jadi potongan max 4000 karakter
max_panjang = 4000
potongan = []
while len(pesan) > max_panjang:
    # Cari titik potong terakhir sebelum 4000 karakter
    potong_di = pesan.rfind("\n", 0, max_panjang)
    if potong_di == -1:
        potong_di = max_panjang
    potongan.append(pesan[:potong_di])
    pesan = pesan[potong_di:].lstrip()

potongan.append(pesan)

# Kirim satu-satu
for i, bagian in enumerate(potongan):
    print(f"Mengirim bagian {i+1} dari {len(potongan)}...")
    r = requests.post(url_tg, data={"chat_id": CHAT_ID, "text": bagian})
    print(f"Status: {r.status_code}")

print("Selesai! Cek Telegram.")
