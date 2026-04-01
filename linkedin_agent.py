import os
import requests
import time
import json

# ==============================
# НАСТРОЙКИ из Railway Variables
# ==============================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "314445281")
WARMYSENDER_API_KEY = os.environ.get("WARMYSENDER_API_KEY")
MODEL = "anthropic/claude-3-5-haiku"

YOUR_NAME = "Дмитрий"
YOUR_EXPERTISE = "премиальная гибкая упаковка для брендов DACH региона (Packitly)"

if not OPENROUTER_API_KEY:
    print("ОШИБКА: OPENROUTER_API_KEY не найден!")
    exit(1)
if not TELEGRAM_BOT_TOKEN:
    print("ОШИБКА: TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

print("Все переменные найдены — Packitly Agent запускается!")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
WARMYSENDER_BASE = "https://warmysender.com/api/v1"

# ==============================
# TELEGRAM: Отправить сообщение
# ==============================
def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# ==============================
# TELEGRAM: Получить обновления
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
    prompt = f"""Ты — {YOUR_NAME}, основатель Packitly, эксперт в области {YOUR_EXPERTISE}.

Прочитай этот пост из LinkedIn и напиши умный, персонализированный комментарий от моего лица.

Правила:
- Длина: 2-4 предложения
- Тон: профессиональный, уверенный (German Business Style)
- Упомяни конкретную деталь из поста
- Определи язык поста и отвечай на том же языке (немецкий или английский)
- НЕ пиши "Nice post!" или банальщину
- Подход: consultative selling, не продавай напрямую

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
    prompt = f"""Ты — эксперт по LinkedIn и B2B продажам упаковки в DACH регионе.

Packitly производит гибкую упаковку (дой-паки, саше, 3D-пакеты) для брендов кофе, снеков, протеина, CBD, pet food, косметики.

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
# ФУНКЦИЯ: Тест WarmySender поиска
# ==============================
def test_warmysender_search(query):
    if not WARMYSENDER_API_KEY:
        return "WARMYSENDER_API_KEY не найден в переменных!"

    headers = {
        "Authorization": f"Bearer {WARMYSENDER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Тестовые ниши Packitly
    test_queries = [
        {"name": "Кофе", "keywords": "Kaffeerösterei Inhaber", "location": "Germany"},
        {"name": "Снеки", "keywords": "Snack Brand Gründer", "location": "Germany"},
        {"name": "Коллаген/Beauty", "keywords": "Collagen Brand Founder", "location": "Germany"},
        {"name": "Протеин", "keywords": "Protein Brand Gründer", "location": "Germany"},
        {"name": "CBD", "keywords": "CBD Brand Inhaber", "location": "Germany"},
    ]

    # Если пользователь указал свой запрос
    if query and query.strip():
        test_queries = [{"name": "Ваш запрос", "keywords": query.strip(), "location": "Germany"}]

    report = "ТЕСТ ПОИСКА WARMYSENDER\n"
    report += "=" * 30 + "\n\n"

    for q in test_queries:
        report += f"Ниша: {q['name']}\n"
        report += f"Keywords: {q['keywords']}\n"

        try:
            # Пробуем найти через LinkedIn search endpoint
            r = requests.get(
                f"{WARMYSENDER_BASE}/prospects/linkedin-search",
                headers=headers,
                params={
                    "keywords": q["keywords"],
                    "location": q["location"],
                    "limit": 3
                },
                timeout=20
            )

            if r.status_code == 200:
                data = r.json()
                prospects = data.get("data", data.get("results", data.get("prospects", [])))

                if isinstance(prospects, list) and len(prospects) > 0:
                    report += f"Найдено: {len(prospects)} чел.\n"
                    for i, p in enumerate(prospects[:3]):
                        name = p.get("name", p.get("firstName", "?") + " " + p.get("lastName", ""))
                        title = p.get("title", p.get("jobTitle", p.get("headline", "—")))
                        company = p.get("company", p.get("companyName", "—"))
                        report += f"  {i+1}. {name}\n     {title}\n     {company}\n"
                else:
                    report += f"Пусто. Ответ: {str(data)[:100]}\n"

            elif r.status_code == 401:
                report += "Ошибка 401: Неверный API ключ\n"
            elif r.status_code == 403:
                report += "Ошибка 403: Нет доступа к этому endpoint\n"
            else:
                report += f"Статус: {r.status_code}\n"
                report += f"Ответ: {r.text[:150]}\n"

        except Exception as e:
            report += f"Ошибка: {str(e)[:100]}\n"

        report += "\n"
        time.sleep(1)

    return report

# ==============================
# ОБРАБОТКА КОМАНД
# ==============================
def handle_message(chat_id, text):
    text = text.strip()

    if text.startswith("/start"):
        send_message(chat_id,
            "Packitly LinkedIn Agent готов!\n\n"
            "Команды:\n"
            "/comment [текст поста] — написать комментарий\n"
            "/analyze [текст поста] — проанализировать пост\n"
            "/testleads — тест поиска лидов по всем нишам\n"
            "/testleads [запрос] — тест своего запроса\n"
            "/help — справка"
        )

    elif text.startswith("/help"):
        send_message(chat_id,
            "Как пользоваться Packitly Agent:\n\n"
            "/comment [текст поста] — Claude пишет комментарий от Дмитрия\n"
            "/analyze [текст поста] — анализ поста как потенциального лида\n"
            "/testleads — тест качества поиска WarmySender по нишам Packitly\n"
            "/testleads Matcha Brand Germany — свой поисковый запрос"
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

    elif text.startswith("/testleads"):
        query = text[10:].strip() if len(text) > 10 else ""
        send_message(chat_id, "Запускаю тест поиска WarmySender... подожди 15-30 секунд")
        report = test_warmysender_search(query)
        send_message(chat_id, report)

    elif text.startswith("/comment") or text.startswith("/analyze"):
        send_message(chat_id,
            "Укажи текст после команды.\n"
            "Пример: /comment Automatisierung ist die Zukunft..."
        )

    else:
        send_message(chat_id,
            "Используй команды:\n"
            "/comment [текст] — комментарий\n"
            "/analyze [текст] — анализ поста\n"
            "/testleads — тест поиска лидов\n"
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
        "Packitly Agent обновлён!\n\n"
        "Новая команда:\n"
        "/testleads — тест поиска лидов WarmySender по всем нишам\n\n"
        "Напиши /testleads чтобы проверить качество поиска!"
    )

    offset = None
    print("Агент слушает команды...")

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if message and "text" in message:
                chat_id = message["chat"]["id"]
                text = message["text"]
                print(f"Получено: {text[:60]}")
                handle_message(chat_id, text)
        time.sleep(1)

if __name__ == "__main__":
    main()
