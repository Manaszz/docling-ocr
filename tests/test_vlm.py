import requests
import json

url = 'http://localhost:8002/ocr/docling/upload'
file_path = r'd:\codding\ai\_RAG\docs\мб-вх-2020-5659_ФГ БУДУЩЕЕ.pdf'

print('=== VLM пайплайн (vlm) с новым API ключом ===')
try:
    with open(file_path, 'rb') as f:
        files = {'file': ('мб-вх-2020-5659_ФГ БУДУЩЕЕ.pdf', f, 'application/pdf')}
        params = {'pipeline': 'vlm'}
        response = requests.post(url, files=files, params=params, timeout=300)

    print(f'HTTP Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        # Показываем основные поля без проблем с кодировкой
        if isinstance(data, list) and len(data) > 0:
            result = data[0]
            print(f"Файл: {result.get('file_name', 'N/A')}")
            print(f"Расширение: {result.get('file_extension', 'N/A')}")
            print(f"Pipeline: {result.get('pipeline_used', 'N/A')}")
            print(f"OCR использован: {result.get('metadata', {}).get('ocr_used', 'N/A')}")
            print(f"Количество страниц: {result.get('metadata', {}).get('num_pages', 'N/A')}")
            print(f"Количество таблиц: {result.get('metadata', {}).get('num_tables', 'N/A')}")
            print(f"Количество картинок: {result.get('metadata', {}).get('num_pictures', 'N/A')}")
            print(f"Длина текста: {len(result.get('file_text', ''))}")
            print("✅ VLM пайплайн работает успешно!")
        else:
            print(json.dumps(data, indent=2))
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Exception: {e}')
