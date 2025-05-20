from openai import OpenAI
import json
import re
from bot import categories
CATEGORIES = sorted(categories.expense_categories)

class ReceiptItemExtractorGPT:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def extract_items(self, ocr_text: str) -> list[dict]:
        example = """
[
  {
    "name": "Смартфон BQ 5565L FEST 2/16GB",
    "price": 4199.0,
    "category": "Подарки"
  }
]
"""
        prompt = f"""
Ты OCR-анализатор чеков. Получи текст OCR и верни список покупок с названием, ценой, категорией, без валюты и только на русском языке.

Категория должна быть строго выбрана из списка:
{", ".join(CATEGORIES)}

⚠️ Формат вывода: JSON-массив как в примере ниже. Никакого текста до или после!

Пример:
{example}

OCR текст:
\"\"\"{ocr_text}\"\"\"
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        try:
            # если GPT вернул текст с ```json — извлекаем только JSON-блок
            json_text = re.search(r"\[.*\]", content, re.DOTALL)
            if json_text:
                return json.loads(json_text.group())
            return json.loads(content)
        except json.JSONDecodeError:
            print("❌ GPT вернул невалидный JSON:")
            
            return []
