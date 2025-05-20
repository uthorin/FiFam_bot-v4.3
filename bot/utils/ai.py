import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def format_amount(amount: float) -> str:
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")


async def generate_financial_analysis(history: list[dict]) -> str:
    """
    Генерирует краткий анализ финансового поведения.
    Разделяет доходы и расходы, форматирует суммы, избегает разметки.
    """
    income = [t for t in history if t.get("type") == "income"]
    expense = [t for t in history if t.get("type") == "expense"]

    def block(title: str, items: list[dict]) -> str:
        lines = [f"- {t['date']}: {t['category']} — {format_amount(t['amount'])}" for t in items]
        return f"{title}:\n" + ("\n".join(lines) if lines else "–")

    prompt = (
        "Ты — финансовый аналитик. Пользователь прислал список транзакций. Раздели их на доходы и расходы. "
        "Проанализируй поведение и предложи конкретные советы. "
        "Не используй форматирование Markdown или HTML. Не указывай валюту. Форматируй суммы с разрядностью и запятой как разделителем копеек.\n\n"
        + block("Доходы", income)
        + "\n\n"
        + block("Расходы", expense)
        + "\n\n"
        "Сделай краткий анализ и дай 2–3 рекомендации. Пиши простым языком, как человеку. Избегай общих фраз и формальных советов."
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
    except Exception as e:
        print(f"❌ Ошибка при генерации анализа: {e}")
        return "❌ Ошибка при генерации анализа. Попробуй позже."

    return response.choices[0].message.content.strip()


async def get_ai_financial_advice(transactions: list[dict]) -> list[str]:
    """
    Пошаговый анализ транзакций с рекомендациями.
    """
    income = [t for t in transactions if t.get("type") == "income"]
    expense = [t for t in transactions if t.get("type") == "expense"]

    def block(title: str, items: list[dict]) -> str:
        return f"{title}:\n" + "\n".join(
            f"{t['date']} — {t['category']} — {format_amount(t['amount'])}"
            for t in items
        )

    prompt = (
        "Ты — финансовый консультант. У тебя список транзакций пользователя.\n"
        "1. Укажи главную категорию расходов.\n"
        "2. Заметь разовые крупные траты.\n"
        "3. Приведи точные цифры: сумма, категория, количество записей.\n"
        "4. Дай 2–3 практичных совета.\n\n"
        "Не используй форматирование Markdown или HTML или валюту. Форматируй суммы разрядно (например: 15 000,00). Пиши как человек, без общих фраз.\n\n"
        + block("Доходы", income)
        + "\n\n"
        + block("Расходы", expense)
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )
    except Exception as e:  
        print(f"❌ Ошибка при генерации анализа: {e}")
        return ["❌ Ошибка при генерации анализа. Попробуй позже."]
    result = response.choices[0].message.content.strip()
    return [s.strip() for s in result.split("\n\n") if s.strip()]