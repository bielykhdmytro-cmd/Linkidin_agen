import os
import requests
import time

# ==============================
# НАСТРОЙКИ из Railway Variables
# ==============================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "314445281")
MODEL = "anthropic/claude-3-5-haiku"

if not OPENROUTER_API_KEY:
    print("ОШИБКА: OPENROUTER_API_KEY не найден!")
    exit(1)
if not TELEGRAM_BOT_TOKEN:
    print("ОШИБКА: TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

print("Все переменные найдены — агент запускается!")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ==============================
# ЗАГРУЗКА ПРОФИЛЯ
# ==============================
def load_profile():
    try:
        with open("profile.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Имя: Дмитрий Белых. Основатель Packitly — премиальная гибкая упаковка для брендов в DACH регионе."

PROFILE = load_profile()
print("Профиль загружен!")

# ==============================
# TELEGRAM: Отправить сообщение
# ==============================
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ==============================
# TELEGRAM: Получить новые сообщения
# ==============================
def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
        return []

# ==============================
# ФУНКЦИЯ: Генерация комментария
# ==============================
def generate_comment(post_text):
    prompt = f"""Ты — Дмитрий Белых, основатель Packitly. Вот твой полный профиль:

{PROFILE}

Прочитай этот пост из LinkedIn и напиши умный, персонализированный комментарий от лица Дмитрия.

Правила:
- Длина: 2-4 предложения
- Тон: профессиональный, уверенный, спокойный (German Business Style)
- Упомяни конкретную деталь из поста — покажи что реально читал
- Если пост связан с твоими индустриями (упаковка, снеки, кофе, протеин, CBD, pet food) — добавь короткий экспертный инсайт
- Определи язык поста и отвечай на том же языке (немецкий или английский)
- НЕ пиши "Nice post!", "Great insight!" или другие банальности
- НЕ продавай напрямую — consultative approach

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
    prompt = f"""Ты — эксперт по LinkedIn и B2B продажам в DACH регионе.

Вот профиль клиента которому нужен анализ:
{PROFILE}

Проанализируй этот пост и ответь кратко:
1. Стоит ли комментировать? (да/нет)
2. Кто автор скорее всего (должность, индустрия)?
3. Это тёплый лид, холодный, или нецелевой для Packitly?
4. Одна причина почему стоит/не стоит комментировать

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
# ОБРАБОТКА КОМАНД
# ==============================
def handle_message(chat_id, text):
    text = text.strip()

    if text.startswith("/start"):
        send_message(chat_id,
            "Packitly LinkedIn Agent готов!\n\n"
            "Команды:\n"
            "/comment [текст поста] — написать комментарий от Дмитрия\n"
            "/analyze [текст поста] — проанализировать пост как лид\n"
            "/help — справка"
        )

    elif text.startswith("/help"):
        send_message(chat_id,
            "Как пользоваться:\n\n"
            "1. Найди пост в LinkedIn от потенциального клиента\n"
            "2. Скопируй текст поста\n"
            "3. Напиши:\n"
            "/comment [вставь текст поста]\n\n"
            "Получишь готовый комментарий на языке поста!\n\n"
            "Используй /analyze чтобы понять стоит ли вообще комментировать."
        )

    elif text.startswith("/comment "):
        post_text = text[9:].strip()
        send_message(chat_id, "Генерирую комментарий от Дмитрия...")
        comment = generate_comment(post_text)
        send_message(chat_id, f"Готовый комментарий:\n\n{comment}\n\nСкопируй и вставь в LinkedIn!")

    elif text.startswith("/analyze "):
        post_text = text[9:].strip()
        send_message(chat_id, "Анализирую пост...")
        analysis = analyze_post(post_text)
        send_message(chat_id, f"Анализ поста:\n\n{analysis}")

    elif text.startswith("/comment") or text.startswith("/analyze"):
        send_message(chat_id,
            "Укажи текст поста после команды.\n"
            "Пример: /comment Wir suchen nach neuen Verpackungslösungen..."
        )

    else:
        send_message(chat_id,
            "Используй команды:\n"
            "/comment [текст] — написать комментарий\n"
            "/analyze [текст] — проанализировать пост\n"
            "/help — справка"
        )

# ==============================
# ГЛАВНЫЙ ЦИКЛ
# ==============================
def main():
    print("=" * 50)
    print("Packitly LinkedIn Agent запущен!")
    print("=" * 50)

    send_message(TELEGRAM_CHAT_ID,
        "Packitly LinkedIn Agent запущен!\n\n"
        "Профиль Дмитрия загружен — теперь комментарии будут написаны как настоящий эксперт по упаковке.\n\n"
        "/comment [текст поста] — написать комментарий\n"
        "/analyze [текст поста] — проанализировать лида\n"
        "/help — справка"
    )

    offset = None
    print("Бот слушает команды...")

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if message and "text" in message:
                chat_id = message["chat"]["id"]
                text = message["text"]
                print(f"Получено: {text[:50]}")
                handle_message(chat_id, text)
        time.sleep(1)

if __name__ == "__main__":
    main()
