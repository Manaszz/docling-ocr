import requests
import json

url = 'http://localhost:8002/ocr/docling/upload'
file_path = r'd:\codding\ai\_RAG\docs\мб-вх-2020-5659_ФГ БУДУЩЕЕ.pdf'

print('=== Стандартный пайплайн (std) ===')
try:
    with open(file_path, 'rb') as f:
        files = {'file': ('мб-вх-2020-5659_ФГ БУДУЩЕЕ.pdf', f, 'application/pdf')}
        params = {'pipeline': 'std'}
        response = requests.post(url, files=files, params=params, timeout=300)

    print(f'HTTP Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Exception: {e}')

print('\n' + '='*50 + '\n')

print('=== VLM пайплайн (vlm) ===')
try:
    with open(file_path, 'rb') as f:
        files = {'file': ('мб-вх-2020-5659_ФГ БУДУЩЕЕ.pdf', f, 'application/pdf')}
        params = {'pipeline': 'vlm'}
        response = requests.post(url, files=files, params=params, timeout=300)

    print(f'HTTP Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Exception: {e}')
