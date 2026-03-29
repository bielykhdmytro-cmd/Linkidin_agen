import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# НАСТРОЙКИ из Railway Variables
# ==============================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "314445281")
MODEL = "anthropic/claude-3-5-haiku"

YOUR_NAME = "Дмитрий"
YOUR_EXPERTISE = "автоматизация бизнес-процессов и AI-инструменты для продаж"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# ПРОВЕРКА ПЕРЕМЕННЫХ
# ==============================
if not OPENROUTER_API_KEY:
    print("ОШИБКА: OPENROUTER_API_KEY не найден!")
    exit(1)
if not TELEGRAM_BOT_TOKEN:
    print("ОШИБКА: TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

print("Все переменные найдены — агент запускается!")

# ==============================
# ФУНКЦИЯ: Генерация комментария
# ==============================
def generate_comment(post_text):
    prompt = f"""Ты — {YOUR_NAME}, эксперт в области {YOUR_EXPERTISE}.

Прочитай этот пост из LinkedIn и напиши умный, персонализированный комментарий от моего лица.

Правила:
- Длина: 2-4 предложения
- Тон: профессиональный, дружелюбный
- Упомяни конкретную деталь из поста
- Определи язык поста и отвечай на том же языке (немецкий или английский)
- НЕ пиши "Nice post!" или банальщину

ПОСТ:
{post_text}

КОММЕНТАРИЙ:"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"

# ==============================
# ФУНКЦИЯ: Анализ поста
# ==============================
def analyze_post(post_text):
    prompt = f"""Ты — эксперт по LinkedIn и B2B продажам на немецком рынке.

Проанализируй этот пост и ответь:
1. Стоит ли его комментировать? (да/нет)
2. Кто автор скорее всего (должность, тип компании)?
3. Это тёплый лид, холодный, или нецелевой?
4. Одна причина почему стоит/не стоит комментировать

Отвечай кратко, по пунктам.

ПОСТ:
{post_text}"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"

# ==============================
# КОМАНДЫ TELEGRAM БОТА
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>LinkedIn Agent готов к работе!</b>\n\n"
        "Доступные команды:\n\n"
        "/comment [текст поста] — написать комментарий\n"
        "/analyze [текст поста] — проанализировать пост\n"
        "/help — показать эту справку\n\n"
        "Просто скопируй текст поста из LinkedIn и отправь мне!",
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Как пользоваться агентом:</b>\n\n"
        "1️⃣ Найди интересный пост в LinkedIn\n"
        "2️⃣ Скопируй текст поста\n"
        "3️⃣ Напиши мне:\n"
        "<code>/comment [вставь текст поста]</code>\n\n"
        "Я напишу готовый комментарий на языке поста!\n\n"
        "Или используй /analyze чтобы проверить стоит ли вообще комментировать.",
        parse_mode="HTML"
    )

async def comment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_text = " ".join(context.args)

    if not post_text:
        await update.message.reply_text(
            "⚠️ Укажи текст поста после команды.\n\n"
            "Пример:\n<code>/comment Автоматизация — это будущее продаж...</code>",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text("⏳ Генерирую комментарий...")

    comment = generate_comment(post_text)

    await update.message.reply_text(
        f"💬 <b>Готовый комментарий:</b>\n\n"
        f"{comment}\n\n"
        f"✅ Скопируй и вставь в LinkedIn!",
        parse_mode="HTML"
    )

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_text = " ".join(context.args)

    if not post_text:
        await update.message.reply_text(
            "⚠️ Укажи текст поста после команды.\n\n"
            "Пример:\n<code>/analyze Автоматизация — это будущее...</code>",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text("🔍 Анализирую пост...")

    analysis = analyze_post(post_text)

    await update.message.reply_text(
        f"📊 <b>Анализ поста:</b>\n\n{analysis}",
        parse_mode="HTML"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Если пользователь просто отправил текст без команды"""
    await update.message.reply_text(
        "Используй команды:\n"
        "/comment [текст] — написать комментарий\n"
        "/analyze [текст] — проанализировать пост\n"
        "/help — справка"
    )

# ==============================
# ЗАПУСК БОТА
# ==============================
def main():
    print("=" * 50)
    print("LinkedIn Agent + Telegram Bot запущен!")
    print("=" * 50)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("comment", comment_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот слушает команды...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
