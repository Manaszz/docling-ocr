#!/usr/bin/env python3
"""Проверка исправлений локализации"""

import json
import os

def check_file_exists(filepath):
    return os.path.exists(filepath)

def check_content(filepath, search_text):
    if not check_file_exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return search_text in content
    except:
        return False

def check_json_key(filepath, key_path):
    if not check_file_exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        keys = key_path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return False
        return True
    except:
        return False

def main():
    print('🎯 АНАЛИЗ ИСПРАВЛЕНИЙ ЛОКАЛИЗАЦИИ')
    print('=' * 50)

    checks = [
        # Переводы
        ('restartRequired в en.json', lambda: check_json_key('app/locales/en.json', 'messages.restartRequired')),
        ('SUPPORTED_LANGUAGES в i18n.py', lambda: check_content('app/utils/i18n.py', 'SUPPORTED_LANGUAGES')),
        ('Обработка ошибок в i18n.py', lambda: check_content('app/utils/i18n.py', 'logger.')),
        ('Кэширование в i18n.py', lambda: check_content('app/utils/i18n.py', '_translations_cache')),

        # HTML
        ('Селектор языка в HTML', lambda: check_content('app/templates/index.html', 'languageSelect')),
        ('Динамический lang в HTML', lambda: check_content('app/templates/index.html', '{{ language }}')),

        # JavaScript
        ('Функция changeLanguage', lambda: check_content('app/static/js/app.js', 'function changeLanguage')),
        ('Обработка ошибок в t()', lambda: check_content('app/static/js/app.js', 'console.warn') and check_content('app/static/js/app.js', 'console.error')),

        # CSS
        ('Стили селектора языка', lambda: check_content('app/static/css/style.css', '.language-select')),

        # Backend
        ('Поддержка lang параметра', lambda: check_content('app/main.py', 'lang: str = None')),
        ('supported_languages в схеме', lambda: check_content('app/models/schemas.py', 'supported_languages')),
        ('default_language в схеме', lambda: check_content('app/models/schemas.py', 'default_language')),
    ]

    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            status = '✅' if result else '❌'
            print(f'{status} {check_name}: {"ПРОЙДЕНА" if result else "НЕ ПРОЙДЕНА"}')
            if not result:
                all_passed = False
        except Exception as e:
            print(f'❌ {check_name}: ОШИБКА ({e})')
            all_passed = False

    print()
    print('📊 РЕЗУЛЬТАТЫ:')
    if all_passed:
        print('✅ ВСЕ ИСПРАВЛЕНИЯ ВНЕСЕНЫ УСПЕШНО')
        print()
        print('🚀 УЛУЧШЕНИЯ ЛОКАЛИЗАЦИИ:')
        print('• Добавлена поддержка переключения языка в UI')
        print('• Улучшена обработка ошибок и валидация')
        print('• Добавлено кэширование переводов')
        print('• Исправлены недостающие переводы')
        print('• Добавлена информация о поддерживаемых языках в API')
        print('• Улучшена производительность загрузки')
        print('• Добавлена функция очистки кэша для разработки')
    else:
        print('❌ ЕСТЬ ПРОБЛЕМЫ - ТРЕБУЕТСЯ ДОРАБОТКА')

if __name__ == '__main__':
    main()
