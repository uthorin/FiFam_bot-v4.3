import re

text = ""
def clean_line(line):
    line = re.sub(r'[^\w\s\[\]/\-.,]', '', line)  # убираем мусор
    return line.strip()

def extract_items_multiline(text: str):
    items = []
    buffer = []
    price_pattern = re.compile(r'(\d+[.,]\d{2})')

    lines = text.splitlines()
    for i, line in enumerate(lines):
        line = clean_line(line)

        # если строка пустая или техническая — пропускаем
        if not line or any(kw in line.lower() for kw in [
            'итог', 'сайт', 'адрес', 'оплате', 'днс', 'ооо', 'ростов', 'фнс', 'налог', 'терминал', 'пин', 'приход'
        ]):
            continue

        # если строка содержит цену — считаем её завершением товара
        if price_pattern.search(line):
            price_match = price_pattern.search(line)
            price = float(price_match.group().replace(',', '.'))

            # формируем название из буфера
            name = ' '.join(buffer).strip().title()
            if len(name) >= 4:
                items.append({
                    "name": name,
                    "price": price
                })
            buffer = []  # очищаем буфер
        else:
            # добавляем строку в буфер названия
            buffer.append(line)

    return items




"""# Тест
items = extract_items_multiline(text)
print("=== Найденные товары ===")
for item in items:
    print(f"- {item['name']} — {item['price']} ")"""