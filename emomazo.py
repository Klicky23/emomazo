import os
import time
import requests
import telebot
from telebot import types

# ===== НАСТРОЙКИ =====
BOT_TOKEN   = "8248862308:AAFdLMHWYykXoEm4KR-T6GoVk9s2SfE_ZWs"
BUTTON_URL  = "https://t.me/send?start=SBQ0-CFrzaHNZjOWIy"
BUTTON_TEXT = "Pay CRYPTO in Telegram"
WELCOME_TEXT = (
    "👋 Welcome my Dear Emotional Masochists!!😍\n\n"
    "Other platforms have restrictions on the content that can be posted, 🤢 so here you will find all my comics without censorship\n\n" 
    "🤤(Hard NTR, Humiliation, R*cePlay)🤤 as well as some comics that will not be posted anywhere except the Telegram group💎\n\n" \
    "There is no censorship in the expressions I use, so that I can properly play on the strings of your masochistic souls)😏\n\n"
    "P.S. Unfortunately, payment is currently only available in Crypto. Write to me in DM if you have any ideas on how to accept payment by card. Thank you."

)

# Картинка:
LOCAL_IMAGE_PATH = "assets/welcome.png"    # положи файл сюда (надёжно)
IMAGE_URL = ""  # или прямая ссылка на .jpg/.png/.webp (оставь пустым, если файла хватает)

# =====================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

def is_image_url(url: str) -> bool:
    if not url:
        return False
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        ct = r.headers.get("Content-Type", "")
        return r.status_code == 200 and ct.startswith("image/")
    except Exception:
        return False

def send_welcome_with_photo(chat_id: int):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(BUTTON_TEXT, url=BUTTON_URL))

    # 1) локальный файл — самый стабильный способ
    if os.path.exists(LOCAL_IMAGE_PATH):
        try:
            with open(LOCAL_IMAGE_PATH, "rb") as f:
                bot.send_photo(chat_id, f, caption=WELCOME_TEXT, reply_markup=kb)
                return
        except Exception:
            pass

    # 2) URL, только если это точно image/*
    if is_image_url(IMAGE_URL):
        try:
            bot.send_photo(chat_id, IMAGE_URL, caption=WELCOME_TEXT, reply_markup=kb)
            return
        except Exception:
            pass

    # 3) только текст
    bot.send_message(chat_id, WELCOME_TEXT, reply_markup=kb, disable_web_page_preview=True)

@bot.message_handler(commands=["start"])
def on_start(message: telebot.types.Message):
    send_welcome_with_photo(message.chat.id)

def start_bot():
    while True:
        try:
            # бесконечный polling с автоперезапуском
            bot.infinity_polling(timeout=90, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("Bot starting…")
    start_bot()