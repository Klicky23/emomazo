import os
import requests
import telebot
from telebot import types
from flask import Flask, request

# === ОБЯЗАТЕЛЬНО: переменная окружения BOT_TOKEN на Render ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env is not set")

# Подставил твой публичный URL с Render из логов
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "https://emomazo.onrender.com")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

# Текст/картинка/кнопка как у тебя
BUTTON_URL  = "https://t.me/send?start=SBQ0-CFrzaHNZjOWIy"
BUTTON_TEXT = "Pay CRYPTO in Telegram"
WELCOME_TEXT = (
    "👋 Welcome my Dear Emotional Masochists!!😍\n\n"
    "Other platforms have restrictions on the content that can be posted, 🤢 so here you will find all my comics without censorship\n\n"
    "🤤(Hard NTR, Humiliation, R*cePlay)🤤 as well as some comics that will not be posted anywhere except the Telegram group💎\n\n"
    "There is no censorship in the expressions I use, so that I can properly play on the strings of your masochistic souls)😏\n\n"
    "P.S. Unfortunately, payment is currently only available in Crypto. Write to me in DM if you have any ideas on how to accept payment by card. Thank you."
)
LOCAL_IMAGE_PATH = "assets/welcome.png"
IMAGE_URL = ""

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

    if os.path.exists(LOCAL_IMAGE_PATH):
        try:
            with open(LOCAL_IMAGE_PATH, "rb") as f:
                bot.send_photo(chat_id, f, caption=WELCOME_TEXT, reply_markup=kb)
                return
        except Exception as e:
            print(f"[photo] local send error: {e}")

    if is_image_url(IMAGE_URL):
        try:
            bot.send_photo(chat_id, IMAGE_URL, caption=WELCOME_TEXT, reply_markup=kb)
            return
        except Exception as e:
            print(f"[photo] url send error: {e}")

    bot.send_message(chat_id, WELCOME_TEXT, reply_markup=kb, disable_web_page_preview=True)

@bot.message_handler(commands=["start"])
def on_start(message: telebot.types.Message):
    send_welcome_with_photo(message.chat.id)

# === Webhook endpoint: Telegram шлёт POST сюда ===
@app.post(WEBHOOK_PATH)
def telegram_update():
    if request.headers.get("content-type") != "application/json":
        return "unsupported", 403
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# health для Render и живости
@app.get("/health")
def health():
    return "ok", 200

# debug: вернуть текущий вебхук и очередь
@app.get("/debug")
def debug():
    info = bot.get_webhook_info()
    return {"url": info.url, "pending": info.pending_update_count}, 200

def ensure_webhook():
    try:
        bot.remove_webhook()
        ok = bot.set_webhook(
            url=WEBHOOK_URL,
            max_connections=40,
            allowed_updates=["message", "callback_query"]
        )
        print(f"[webhook] set={ok} url={WEBHOOK_URL}")
    except Exception as e:
        print(f"[webhook] error: {e}")

# Ставим вебхук сразу при старте, без похода на "/"
ensure_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)