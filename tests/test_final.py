import requests
import json

url = 'http://localhost:8002/ocr/docling/upload'
file_path = r'd:\codding\ai\_RAG\docs\pamyatka.docx'

print('=== Финальное тестирование с .env файлом ===')

# Тест стандартного пайплайна
print('\n--- Стандартный пайплайн (std) ---')
try:
    with open(file_path, 'rb') as f:
        files = {'file': ('pamyatka.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        params = {'pipeline': 'std'}
        response = requests.post(url, files=files, params=params, timeout=300)

    print(f'HTTP Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            result = data[0]
            print(f"[OK] Pipeline: {result.get('pipeline_used', 'N/A')}")
            print(f"[OK] OCR: {result.get('metadata', {}).get('ocr_used', 'N/A')}")
            print(f"[OK] Длина текста: {len(result.get('file_text', ''))}")
    else:
        print(f'[ERROR] Error: {response.text}')
except Exception as e:
    print(f'[ERROR] Exception: {e}')

# Тест VLM пайплайна
print('\n--- VLM пайплайн (vlm) ---')
try:
    with open(file_path, 'rb') as f:
        files = {'file': ('pamyatka.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        params = {'pipeline': 'vlm'}
        response = requests.post(url, files=files, params=params, timeout=300)

    print(f'HTTP Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            result = data[0]
            print(f"[OK] Pipeline: {result.get('pipeline_used', 'N/A')}")
            print(f"[OK] OCR: {result.get('metadata', {}).get('ocr_used', 'N/A')}")
            print(f"[OK] Длина текста: {len(result.get('file_text', ''))}")
    else:
        print(f'[ERROR] Error: {response.text}')
except Exception as e:
    print(f'[ERROR] Exception: {e}')

print('\n[SUCCESS] Тестирование завершено!')
