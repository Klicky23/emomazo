import os
import telebot
from telebot import types
from flask import Flask, request

# ========= CONFIG =========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env is not set")

PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://emomazo.onrender.com")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL  = PUBLIC_URL + WEBHOOK_PATH

# ====== CONTENT ======
BUTTON_URL  = "https://t.me/send?start=SBQ0-CFrzaHNZjOWIy"
BUTTON_TEXT = "Pay CRYPTO in Telegram"
WELCOME_TEXT = (
    "👋 Welcome my Dear Emotional Masochists!!😍\n\n"
    "Other platforms have restrictions on the content that can be posted, 🤢 so here you will find all my comics without censorship\n\n"
    "🤤(Hard NTR, Humiliation, R*cePlay)🤤 as well as some comics that will not be posted anywhere except the Telegram group💎\n\n"
    "There is no censorship in the expressions I use, so that I can properly play on the strings of your masochistic souls)😏\n\n"
    "P.S. Unfortunately, payment is currently only available in Crypto. Write to me in DM if you have any ideas on how to accept payment by card. Thank you."
)
LOCAL_IMAGE_PATH = "assets/welcome.png"   # положи файл в репозиторий
IMAGE_URL = ""                            # можно указать прямую ссылку на картинку
TELEGRAM_MAX_CAPTION = 1024

# ====== INIT ======
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
app = Flask(__name__)

# ====== HELPERS ======
def split_caption(text: str):
    if len(text) <= TELEGRAM_MAX_CAPTION:
        return text, ""
    return text[:TELEGRAM_MAX_CAPTION], text[TELEGRAM_MAX_CAPTION:]

def kb_pay():
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton(BUTTON_TEXT, url=BUTTON_URL))
    return k

def send_text(chat_id: int, text: str, with_button: bool = True):
    try:
        bot.send_message(chat_id, text, reply_markup=(kb_pay() if with_button else None), disable_web_page_preview=True)
        print(f"[send] text ok -> {chat_id}", flush=True)
    except Exception as e:
        print(f"[send] text error -> {chat_id}: {e}", flush=True)

def send_photo_then_text(chat_id: int):
    caption, tail = split_caption(WELCOME_TEXT)

    # 1) локальный файл
    if os.path.exists(LOCAL_IMAGE_PATH):
        try:
            with open(LOCAL_IMAGE_PATH, "rb") as f:
                bot.send_photo(chat_id, f, caption=caption, reply_markup=kb_pay())
            print(f"[send] photo(local) ok -> {chat_id}", flush=True)
            if tail:
                send_text(chat_id, tail, with_button=False)
            return
        except Exception as e:
            print(f"[send] photo(local) error -> {chat_id}: {e}", flush=True)

    # 2) url
    if IMAGE_URL:
        try:
            bot.send_photo(chat_id, IMAGE_URL, caption=caption, reply_markup=kb_pay())
            print(f"[send] photo(url) ok -> {chat_id}", flush=True)
            if tail:
                send_text(chat_id, tail, with_button=False)
            return
        except Exception as e:
            print(f"[send] photo(url) error -> {chat_id}: {e}", flush=True)

    # 3) только текст (фоллбек)
    send_text(chat_id, WELCOME_TEXT, with_button=True)

# ====== HANDLERS ======
@bot.message_handler(commands=["start"])
def on_start(m: telebot.types.Message):
    print(f"[update] /start from {m.from_user.id}", flush=True)
    send_photo_then_text(m.chat.id)

@bot.message_handler(func=lambda m: True)
def on_any(m: telebot.types.Message):
    print(f"[update] msg from {m.from_user.id}: {m.text!r}", flush=True)
    try:
        bot.reply_to(m, "✅ Bot is alive (webhook). Send /start")  # если не нужно — можно убрать эту строку
    except Exception as e:
        print(f"[send] reply error -> {m.chat.id}: {e}", flush=True)

# ====== WEBHOOK ENDPOINT ======
@app.post(WEBHOOK_PATH)
def webhook_handler():
    raw = request.get_data(as_text=True)
    print(f"[raw] {raw}", flush=True)

    # только прокидываем событие в TeleBot (без самостоятельных ответов)
    try:
        upd = telebot.types.Update.de_json(raw)
        bot.process_new_updates([upd])
    except Exception as e:
        print(f"[webhook] process error: {e}", flush=True)

    return "ok", 200

# ====== HEALTH/DEBUG/ROOT ======
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

@app.get("/")
def root():
    return "ok", 200

# ====== SET WEBHOOK ON START ======
def ensure_webhook():
    try:
        bot.remove_webhook()
        ok = bot.set_webhook(
            url=WEBHOOK_URL,
            max_connections=40,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,
        )
        print(f"[webhook] set={ok} url set", flush=True)
    except Exception as e:
        print(f"[webhook] set error: {e}", flush=True)

ensure_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)