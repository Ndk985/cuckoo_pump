import os
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from telegram.helpers import escape_markdown
from markdownify import markdownify as md
from dotenv import load_dotenv

# -------------------- Загрузка настроек --------------------
load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
FLASK_HOST = os.getenv("FLASK_HOST", "http://web:8000")

# -------------------- Кнопка старт --------------------
START_KB = [
    [InlineKeyboardButton("Начать квиз 🎯", callback_data="start_quiz")]
    ]


# -------------------- /start --------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение с кнопкой для запуска квиза"""
    print(f"start command received from user {update.effective_user.id}", flush=True)
    keyboard = InlineKeyboardMarkup(START_KB)
    await update.message.reply_text(
        "Привет! Этот бот позволяет пройти квиз из 10 вопросов.\n\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=keyboard
    )


# -------------------- Запуск квиза --------------------
async def quiz_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Инициализация квиза и отправка первого вопроса"""
    print("quiz_start called", flush=True)
    # callback_query при нажатии кнопки
    query = update.callback_query
    if query:
        print(f"Callback query received: {query.data}", flush=True)
        await query.answer()
    else:
        print("No callback query, this is a message", flush=True)

    # Получаем все id вопросов
    try:
        print(f"Requesting questions from {FLASK_HOST}/api/questions/", flush=True)
        r = requests.get(f"{FLASK_HOST}/api/questions/", timeout=10)
        print(f"Response status: {r.status_code}", flush=True)
        r.raise_for_status()
        all_questions = r.json()["questions"]
        print(f"Got {len(all_questions)} questions", flush=True)
        all_ids = [q["id"] for q in all_questions]
    except Exception as e:
        print(
            "Ошибка при получении списка вопросов для квиза:",
            repr(e),
            flush=True
        )
        import traceback
        traceback.print_exc()
        if query:
            await query.message.reply_text("Не удалось начать квиз 😥")
        else:
            await update.message.reply_text("Не удалось начать квиз 😥")
        return

    if not all_ids:
        if query:
            await query.message.reply_text("В базе нет вопросов 😥")
        else:
            await update.message.reply_text("В базе нет вопросов 😥")
        return

    # Формируем 10 уникальных или меньше
    k = min(10, len(all_ids))
    quiz_ids = random.sample(all_ids, k=k)

    # Сохраняем прогресс в user_data
    ctx.user_data['quiz_ids'] = quiz_ids
    ctx.user_data['quiz_index'] = 0
    ctx.user_data['quiz_correct'] = 0
    ctx.user_data['quiz_total'] = k

    # Отправляем первый вопрос
    await send_quiz_question(update, ctx)


# -------------------- Отправка вопроса --------------------
async def send_quiz_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    idx = ctx.user_data['quiz_index']
    q_id = ctx.user_data['quiz_ids'][idx]

    try:
        r = requests.get(f"{FLASK_HOST}/api/questions/{q_id}/", timeout=10)
        r.raise_for_status()
        question = r.json()["question"]
    except Exception as e:
        print("Ошибка при получении вопроса для квиза:", repr(e), flush=True)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "Ошибка при загрузке вопроса 😥"
            )
        else:
            await update.message.reply_text("Ошибка при загрузке вопроса 😥")
        return

    # Кнопки "Знаю / Не знаю"
    keyboard = [
        [
            InlineKeyboardButton("Знаю ✅", callback_data="know"),
            InlineKeyboardButton("Не знаю ❌", callback_data="dont_know"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем текст вопроса
    text_safe = escape_markdown(question["title"], version=2)
    print(f"Sending question {q_id}: {question['title'][:50]}...", flush=True)
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                text_safe, reply_markup=reply_markup, parse_mode="MarkdownV2"
            )
        else:
            await update.message.reply_text(
                text_safe, reply_markup=reply_markup, parse_mode="MarkdownV2"
            )
        print("Question sent successfully", flush=True)
    except Exception as e:
        print(f"Error sending question: {repr(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise


# -------------------- Обработка "Знаю / Не знаю" --------------------
async def quiz_answer_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data['last_answer'] = query.data  # "know" или "dont_know"

    idx = ctx.user_data['quiz_index']
    q_id = ctx.user_data['quiz_ids'][idx]

    # Получаем полный ответ на вопрос
    try:
        r = requests.get(f"{FLASK_HOST}/api/questions/{q_id}/", timeout=10)
        r.raise_for_status()
        question = r.json()["question"]
    except Exception as e:
        print("Ошибка при получении ответа для квиза:", repr(e), flush=True)
        await query.message.reply_text("Ошибка при загрузке ответа 😥")
        return

    # Подготовка текста
    text_md = md(question["text"]).strip()
    full_text = f"*{escape_markdown(question['title'], version=2)}*\n\n{escape_markdown(text_md, version=2)}"

    # Кнопки "Ответил / Нужно подучить"
    keyboard = [
        [
            InlineKeyboardButton("Ответил ✅", callback_data="answered"),
            InlineKeyboardButton("Нужно подучить ❌", callback_data="review"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Разбиваем длинный текст на блоки
    MAX_LEN = 4000
    chunks = [
        full_text[i:i+MAX_LEN] for i in range(0, len(full_text), MAX_LEN)
    ]

    # Отправляем каждый блок, кнопки только под последним
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await query.message.reply_text(
                chunk, reply_markup=reply_markup, parse_mode="MarkdownV2"
            )
        else:
            await query.message.reply_text(chunk, parse_mode="MarkdownV2")


# -------------------- Обработка "Ответил / Нужно подучить" -------------------
async def quiz_mark_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data  # "answered" или "review"

    if action == "answered":
        ctx.user_data['quiz_correct'] += 1

    # Переходим к следующему вопросу
    ctx.user_data['quiz_index'] += 1
    if ctx.user_data['quiz_index'] >= ctx.user_data['quiz_total']:
        # Конец квиза
        correct = ctx.user_data['quiz_correct']
        total = ctx.user_data['quiz_total']

        keyboard = [
            [InlineKeyboardButton("Пройти ещё раз 🔄", callback_data="restart")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            f"Квиз завершён! ✅ {correct} / {total} правильных ответов.",
            reply_markup=reply_markup
        )
    else:
        # Следующий вопрос
        await send_quiz_question(update, ctx)


# -------------------- Обработка "Пройти ещё раз" --------------------
async def quiz_restart_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await quiz_start(update, ctx)


# -------------------- Запуск бота --------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    # Универсальный обработчик для всех callback_query
    async def all_callbacks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            print(f"DEBUG: Callback received: {query.data} from user {query.from_user.id}", flush=True)
            await query.answer()  # Всегда отвечаем на callback
            
            # Маршрутизация по типу callback
            if query.data == "start_quiz":
                await quiz_start(update, ctx)
            elif query.data in ["know", "dont_know"]:
                await quiz_answer_handler(update, ctx)
            elif query.data in ["answered", "review"]:
                await quiz_mark_handler(update, ctx)
            elif query.data == "restart":
                await quiz_restart_handler(update, ctx)
            else:
                print(f"DEBUG: Unknown callback data: {query.data}", flush=True)
                await query.message.reply_text("Неизвестная команда")
        else:
            print("DEBUG: No callback_query in update", flush=True)
    
    # Используем один универсальный обработчик для всех callback
    app.add_handler(CallbackQueryHandler(all_callbacks))

    # Обработчик ошибок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок для логирования"""
        print(f"Exception while handling an update: {context.error}", flush=True)
        import traceback
        traceback.print_exc()
        
        if isinstance(update, Update) and update.callback_query:
            try:
                await update.callback_query.answer("Произошла ошибка 😥")
            except:
                pass

    app.add_error_handler(error_handler)

    # Очищаем webhook и старые обновления перед запуском polling
    async def post_init(app: Application) -> None:
        bot = app.bot
        try:
            # Сбрасываем webhook, если он был установлен
            await bot.delete_webhook(drop_pending_updates=True)
            print("Webhook cleared, old updates dropped", flush=True)
        except Exception as e:
            print(f"Warning: Could not clear webhook: {e}", flush=True)

    app.post_init = post_init

    print("Bot polling…", flush=True)
    print(f"Bot token set: {TOKEN is not None}", flush=True)
    print(f"Flask host: {FLASK_HOST}", flush=True)
    print("Handlers registered:", flush=True)
    print(f"  - CommandHandler: start", flush=True)
    print(f"  - CallbackQueryHandler: all_callbacks", flush=True)
    
    try:
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
    except Exception as e:
        print(f"Error starting bot: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
