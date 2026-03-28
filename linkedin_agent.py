import requests
import time

# ==============================
# НАСТРОЙКИ
# ==============================
OPENROUTER_API_KEY = "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"
MODEL = "anthropic/claude-3-5-haiku"

# ==============================
# ТВОЙ ПРОФИЛЬ
# ==============================
YOUR_NAME = "Дмитрий"
YOUR_EXPERTISE = "автоматизация бизнес-процессов и AI-инструменты для продаж"

# ==============================
# ФУНКЦИЯ: Генерация комментария
# ==============================
def generate_comment(post_text):
    prompt = f"""Ты — {YOUR_NAME}, эксперт в области {YOUR_EXPERTISE}.

Прочитай этот пост из LinkedIn и напиши умный, персонализированный комментарий от моего лица.

Правила комментария:
- Длина: 2-4 предложения
- Тон: профессиональный, дружелюбный
- Упомяни конкретную деталь из поста (покажи что реально читал)
- Можно добавить короткий инсайт из своего опыта
- НЕ пиши "Nice post!" или банальщину
- Определи язык поста и отвечай на том же языке (немецкий или английский)

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
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    result = response.json()
    return result["choices"][0]["message"]["content"]


# ==============================
# ГЛАВНЫЙ ЦИКЛ (работает 24/7)
# ==============================
if __name__ == "__main__":
    print("=" * 50)
    print("LinkedIn Agent запущен и работает 24/7")
    print("=" * 50)

    # Тестовый пост для проверки
    test_post = """
    Automatisierung bedeutet nicht, Menschen zu ersetzen.
    Es geht darum, dass Menschen sich auf das Wesentliche 
    konzentrieren können. Wir haben 80% unserer Sales-Prozesse 
    automatisiert und sind ohne neue Mitarbeiter um das 3-fache gewachsen.
    """

    print("\nЗапускаем тест с немецким постом...")
    comment = generate_comment(test_post)
    print("\nКОММЕНТАРИЙ ОТ CLAUDE:")
    print(comment)
    print("\n" + "=" * 50)
    print("Агент готов к работе. Ожидаю задачи...\n")

    # Бесконечный цикл — держит сервер живым
    while True:
        print("Агент активен... следующая проверка через 60 минут")
        time.sleep(3600)
