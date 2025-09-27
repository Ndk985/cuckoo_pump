import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown
from markdownify import markdownify as md
from dotenv import load_dotenv

# -------------------- Загрузка настроек --------------------
load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
FLASK_HOST = os.getenv("FLASK_HOST", "http://web:8000")  # Можно переопределить через .env

# -------------------- Постоянная клавиатура --------------------
MAIN_KB = ReplyKeyboardMarkup(
    [[KeyboardButton("Новый вопрос")]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# -------------------- Команда /start --------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажмите «Новый вопрос», чтобы получить случайный вопрос.",
        reply_markup=MAIN_KB
    )

# -------------------- Обработчик текстовых сообщений --------------------
async def question_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Новый вопрос":
        try:
            r = requests.get(f"{FLASK_HOST}/api/get-random-question/", timeout=10)
            r.raise_for_status()
            data = r.json()["opinion"]

            # Конвертация HTML → Markdown
            text_md = md(data["text"]).strip()

            # Экранируем спецсимволы для Telegram MarkdownV2
            title_safe = escape_markdown(data["title"], version=2)
            text_safe = escape_markdown(text_md, version=2)
            md_text = f"*{title_safe}*\n\n{text_safe}"

            try:
                # Отправка с MarkdownV2
                await update.message.reply_markdown_v2(md_text, reply_markup=MAIN_KB)
            except Exception as markdown_error:
                # Fallback plain-text
                print("MarkdownV2 не сработал, fallback plain-text:", repr(markdown_error), flush=True)
                await update.message.reply_text(
                    f"{data['title']}\n\n{md(data['text']).strip()}",
                    reply_markup=MAIN_KB
                )

        except Exception as e:
            print("Ошибка при получении вопроса:", repr(e), flush=True)
            await update.message.reply_text(
                "Не удалось получить вопрос 😥", reply_markup=MAIN_KB
            )

# -------------------- Запуск бота --------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler))
    print("Bot polling…")
    app.run_polling()

if __name__ == "__main__":
    main()
