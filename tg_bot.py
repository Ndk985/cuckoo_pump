import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv("TG_BOT_TOKEN")
FLASK_HOST = "http://127.0.0.1:5000"


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажмите /question и получите случайный вопрос по Python."
    )


async def random_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(f"{FLASK_HOST}/api/get-random-question/", timeout=5)
        r.raise_for_status()
        data = r.json()["opinion"]
        text = f"*{data['title']}*\n\n{data['text']}"
        await update.message.reply_markdown(text)
    except Exception as e:
        await update.message.reply_text("Не удалось получить вопрос 😥")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("question", random_question))
    print("Bot polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
