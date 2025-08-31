import os
import requests
import telebot
from telebot import types
from flask import Flask, request

# ===== НАСТРОЙКИ =====
BOT_TOKEN   = "8248862308:AAFdLMHWYykXoEm4KR-T6GoVk9s2SfE_ZWs"
BUTTON_URL  = "https://t.me/send?start=SBQ0-CFrzaHNZjOWIy"
BUTTON_TEXT = "Pay CRYPTO in Telegram"
WELCOME_TEXT = (
    "👋 Welcome my Dear Emotional Masochists!!😍\n\n"
    "Other platforms have restrictions on the content that can be posted, 🤢 so here you will find all my comics without censorship\n\n"
    "🤤(Hard NTR, Humiliation, R*cePlay)🤤 as well as some comics that will not be posted anywhere except the Telegram group💎\n\n"
    "There is no censorship in the expressions I use, so that I can properly play on the strings of your masochistic souls)😏\n\n"
    "P.S. Unfortunately, payment is currently only available in Crypto. Write to me in DM if you have any ideas on how to accept payment by card. Thank you."
)

LOCAL_IMAGE_PATH = "assets/welcome.png"   # файл положи сюда
IMAGE_URL = ""                            # если хочешь прямой URL — укажи здесь
WEBHOOK_HOST = "https://ТВОЙ-СЕРВИС.onrender.com"  # ← замени на Render URL
WEBHOOK_PATH = "/" + BOT_TOKEN
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
# =====================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)


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

    # 1) Локальная картинка
    if os.path.exists(LOCAL_IMAGE_PATH):
        try:
            with open(LOCAL_IMAGE_PATH, "rb") as f:
                bot.send_photo(chat_id, f, caption=WELCOME_TEXT, reply_markup=kb)
                return
        except Exception:
            pass

    # 2) По URL
    if is_image_url(IMAGE_URL):
        try:
            bot.send_photo(chat_id, IMAGE_URL, caption=WELCOME_TEXT, reply_markup=kb)
            return
        except Exception:
            pass

    # 3) Только текст
    bot.send_message(chat_id, WELCOME_TEXT, reply_markup=kb, disable_web_page_preview=True)


@bot.message_handler(commands=["start"])
def on_start(message: telebot.types.Message):
    send_welcome_with_photo(message.chat.id)


# === Flask Webhook ===
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("UTF-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "ok", 200
    return "unsupported", 403


@app.route("/", methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Webhook set!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)