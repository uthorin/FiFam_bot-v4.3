import os
from google.cloud import vision
from dotenv import load_dotenv

load_dotenv()

def run_ocr_google(image_path: str) -> str:
    try:
        client = vision.ImageAnnotatorClient()

        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        texts = response.text_annotations
        if not texts:
            return "[Пусто]"

        return texts[0].description  # полный текст

    except Exception as e:
        return f"[Ошибка]: {e}"

# Запуск
'''if __name__ == "__main__":
    result = run_ocr_google("check1.jpg")  # замени на свой файл
    print("=== Результат OCR ===")
    print(result)'''
