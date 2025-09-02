import os
import requests
from markdownify import markdownify as md
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
FLASK_HOST = "http://127.0.0.1:5000"

# ---------- постоянная клавиатура ----------
MAIN_KB = ReplyKeyboardMarkup(
    [[KeyboardButton("Новый вопрос")]],
    resize_keyboard=True,
    one_time_keyboard=False
)


# ---------- команды ----------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажмите «Новый вопрос», чтобы получить случайный вопрос.",
        reply_markup=MAIN_KB
    )


# ---------- обработчик текстовых сообщений ----------
async def question_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Новый вопрос":
        try:
            r = requests.get(f"{FLASK_HOST}/api/get-random-question/", timeout=5)
            r.raise_for_status()
            data = r.json()["opinion"]
            md_text = f"*{md(data['title']).strip()}*\n\n{md(data['text']).strip()}"
            await update.message.reply_markdown(md_text, reply_markup=MAIN_KB)
        except Exception:
            await update.message.reply_text("Не удалось получить вопрос 😥", reply_markup=MAIN_KB)


# ---------- запуск ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler))
    print("Bot polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
