import os
import requests
import telebot
from telebot import types
from flask import Flask, request

# === Конфиг ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env is not set")

PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://emomazo.onrender.com")  # можно переопределить в env
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = PUBLIC_URL + WEBHOOK_PATH

BUTTON_URL  = "https://t.me/send?start=SBQ0-CFrzaHNZjOWIy"
BUTTON_TEXT = "Pay CRYPTO in Telegram"
WELCOME_TEXT = (
    "👋 Welcome my Dear Emotional Masochists!!😍\n\n"
    "Other platforms have restrictions on the content that can be posted, 🤢 so here you will find all my comics without censorship\n\n"
    "🤤(Hard NTR, Humiliation, R*cePlay)🤤 as well as some comics that will not be posted anywhere except the Telegram group💎\n\n"
    "There is no censorship in the expressions I use, so that I can properly play on the strings of your masochistic souls)😏\n\n"
    "P.S. Unfortunately, payment is currently only available in Crypto. Write to me in DM if you have any ideas on how to accept payment by card. Thank you."
)
LOCAL_IMAGE_PATH = "assets/welcome.png"   # если файла нет — просто проигнорим
IMAGE_URL = ""                            # можно указать прямую ссылку на картинку

# === Инициализация ===
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)

def is_image_url(url: str) -> bool:
    if not url:
        return False
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        ct = r.headers.get("Content-Type", "")
        return r.status_code == 200 and ct.startswith("image/")
    except Exception as e:
        print(f"[img-check] error: {e}")
        return False

def send_welcome(chat_id: int):
    # сначала — текст (чтобы гарантированно был ответ)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(BUTTON_TEXT, url=BUTTON_URL))
    try:
        bot.send_message(chat_id, WELCOME_TEXT, reply_markup=kb, disable_web_page_preview=True)
        print(f"[send] text ok -> chat {chat_id}")
    except Exception as e:
        print(f"[send] text error -> chat {chat_id}: {e}")

    # доп. попытка — картинка (если есть)
    try:
        if os.path.exists(LOCAL_IMAGE_PATH):
            with open(LOCAL_IMAGE_PATH, "rb") as f:
                bot.send_photo(chat_id, f)
                print(f"[send] photo local ok -> chat {chat_id}")
                return
        if is_image_url(IMAGE_URL):
            bot.send_photo(chat_id, IMAGE_URL)
            print(f"[send] photo url ok -> chat {chat_id}")
    except Exception as e:
        print(f"[send] photo error -> chat {chat_id}: {e}")

@bot.message_handler(commands=["start"])
def on_start(message: telebot.types.Message):
    print(f"[update] /start from {message.from_user.id}")
    send_welcome(message.chat.id)

# Ответ на любое сообщение — чтобы сразу видеть жизнь
@bot.message_handler(func=lambda m: True)
def on_any(message: telebot.types.Message):
    print(f"[update] msg from {message.from_user.id}: {message.text!r}")
    try:
        bot.reply_to(message, "✅ Bot is alive (webhook). Send /start")
    except Exception as e:
        print(f"[send] reply error -> chat {message.chat.id}: {e}")

# === Webhook endpoint ===
@app.post(WEBHOOK_PATH)
def webhook_handler():
    if request.headers.get("content-type") != "application/json":
        return "unsupported", 403
    data = request.get_data().decode("utf-8")
    try:
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
        return "ok", 200
    except Exception as e:
        print(f"[webhook] process error: {e}")
        return "err", 200  # 200, чтобы TG не ретраил бесконечно

# health/debug
@app.get("/health")
def health():
    return "ok", 200

@app.get("/debug")
def debug():
    try:
        info = bot.get_webhook_info()
        me = bot.get_me()
        return {
            "me": {"id": me.id, "username": me.username},
            "url": info.url,
            "pending": info.pending_update_count,
            "last_error_date": getattr(info, "last_error_date", None),
            "last_error_message": getattr(info, "last_error_message", None),
        }, 200
    except Exception as e:
        return {"error": str(e)}, 200

def ensure_webhook():
    try:
        bot.remove_webhook()
        ok = bot.set_webhook(
            url=WEBHOOK_URL,
            max_connections=40,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,  # не теряем входящие
        )
        print(f"[webhook] set={ok} url={WEBHOOK_URL}")
    except Exception as e:
        print(f"[webhook] set error: {e}")

# ставим webhook при старте
ensure_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)