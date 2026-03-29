import requests
import time
import os

# ==============================
# НАСТРОЙКИ из Railway Variables
# ==============================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "314445281")
MODEL = "anthropic/claude-3-5-haiku"

# ==============================
# ТВОЙ ПРОФИЛЬ
# ==============================
YOUR_NAME = "Дмитрий"
YOUR_EXPERTISE = "автоматизация бизнес-процессов и AI-инструменты для продаж"

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
# ФУНКЦИЯ: Отправка в Telegram
# ==============================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })
    result = response.json()
    if result.get("ok"):
        print("Сообщение отправлено в Telegram!")
    else:
        print(f"Ошибка Telegram: {result}")
    return result

# ==============================
# ФУНКЦИЯ: Генерация комментария
# ==============================
def generate_comment(post_text, author_name=""):
    prompt = f"""Ты — {YOUR_NAME}, эксперт в области {YOUR_EXPERTISE}.

Прочитай этот пост из LinkedIn и напиши умный, персонализированный комментарий от моего лица.

Правила комментария:
- Длина: 2-4 предложения
- Тон: профессиональный, дружелюбный
- Упомяни конкретную деталь из поста
- Определи язык поста и отвечай на том же языке (немецкий или английский)
- НЕ пиши "Nice post!" или банальщину
- Если знаешь имя автора ({author_name}), обратись к нему лично

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
    elif "error" in result:
        return f"Ошибка API: {result['error']}"
    else:
        return f"Неожиданный ответ: {result}"

# ==============================
# ФУНКЦИЯ: Обработка поста
# ==============================
def process_post(post_text, author_name="", post_url=""):
    print(f"\nАнализируем пост от: {author_name}")

    comment = generate_comment(post_text, author_name)

    # Формируем сообщение для Telegram
    message = f"""🤖 <b>LinkedIn Agent — новый комментарий готов!</b>

👤 <b>Автор поста:</b> {author_name if author_name else 'Неизвестен'}
🔗 <b>Ссылка:</b> {post_url if post_url else 'Не указана'}

📝 <b>Текст поста:</b>
{post_text[:300]}{'...' if len(post_text) > 300 else ''}

💬 <b>Готовый комментарий:</b>
{comment}

✅ Скопируй комментарий и опубликуй вручную в LinkedIn!"""

    send_telegram(message)
    return comment

# ==============================
# ГЛАВНЫЙ ЦИКЛ (работает 24/7)
# ==============================
if __name__ == "__main__":
    print("=" * 50)
    print("LinkedIn Agent + Telegram Bot запущен!")
    print("=" * 50)

    # Приветственное сообщение в Telegram
    send_telegram("""🚀 <b>LinkedIn Agent запущен и работает 24/7!</b>

Я буду анализировать посты и отправлять тебе готовые комментарии сюда.

Твоя задача — только скопировать и вставить в LinkedIn.

Первый тест запускается прямо сейчас...""")

    # Тестовый пост
    test_post = """Automatisierung bedeutet nicht, Menschen zu ersetzen.
Es geht darum, dass Menschen sich auf das Wesentliche 
konzentrieren können. Wir haben 80% unserer Sales-Prozesse 
automatisiert und sind ohne neue Mitarbeiter um das 3-fache gewachsen."""

    process_post(
        post_text=test_post,
        author_name="Klaus Müller",
        post_url="https://linkedin.com/posts/example"
    )

    print("\nАгент готов. Жду следующий цикл...\n")

    # Бесконечный цикл — держит сервер живым
    while True:
        print("Агент активен...")
        time.sleep(3600)
