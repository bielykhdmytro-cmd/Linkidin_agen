import requests

# ==============================
# НАСТРОЙКИ
# ==============================
OPENROUTER_API_KEY = "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"
MODEL = "anthropic/claude-3-5-haiku"

# ==============================
# ТВОЙ ПРОФИЛЬ (заполни под себя)
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
- Пиши на том же языке что и пост

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
# ЗАПУСК
# ==============================
if __name__ == "__main__":
    print("=" * 50)
    print("LinkedIn Comment Generator — powered by Claude")
    print("=" * 50)

    # Вставь сюда текст поста для теста
    test_post = """
    Автоматизация — это не про замену людей. 
    Это про то, чтобы люди занимались тем, что важно, 
    а рутину отдавали машинам. За последний год мы 
    автоматизировали 80% нашего sales-процесса и выросли 
    в 3 раза без найма новых людей.
    """

    print("\nПОСТ:")
    print(test_post)
    print("\nГЕНЕРИРУЕМ КОММЕНТАРИЙ...\n")

    comment = generate_comment(test_post)

    print("КОММЕНТАРИЙ ОТ CLAUDE:")
    print(comment)
    print("\n" + "=" * 50)
