import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Tokenul sau chat_id lipsește. Nu trimit notificare.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, data=data)
        if response.ok:
            print("✅ Notificare Telegram trimisă.")
        else:
            print("❌ Eroare la trimiterea notificării:", response.text)
    except Exception as e:
        print("❌ Excepție la trimitere:", str(e))
