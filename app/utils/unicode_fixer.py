"""
Утилита для исправления Unicode-кодов в текстах.

Исправляет коды типа /uni043F (которые появляются при неправильной обработке
PDF-файлов с кириллицей) на соответствующие Unicode-символы.
"""

import re
import logging

logger = logging.getLogger(__name__)


def decode_unicode_code(match) -> str:
    """
    Преобразует код /uniXXXX в соответствующий Unicode-символ.
    
    Args:
        match: объект Match с найденным кодом
        
    Returns:
        Соответствующий Unicode-символ
    """
    hex_code = match.group(1)
    try:
        # Преобразуем hex-код в число и затем в символ
        char_code = int(hex_code, 16)
        return chr(char_code)
    except (ValueError, OverflowError):
        # Если не удалось преобразовать, возвращаем исходный код
        logger.warning(f"Не удалось преобразовать код /uni{hex_code}")
        return match.group(0)


def fix_unicode_codes(text: str) -> str:
    """
    Заменяет все коды /uniXXXX на соответствующие символы в тексте.
    
    Эта функция исправляет распространенную проблему, когда при обработке
    PDF-файлов с кириллицей (особенно со встроенными шрифтами) вместо
    символов появляются их Unicode-коды в формате /uniXXXX.
    
    Причины появления таких кодов:
    1. PDF содержит встроенные шрифты с custom encoding (не Unicode)
    2. OCR-движок некорректно распознает кириллические символы
    3. Промежуточное представление PDF использует PostScript имена глифов
    4. Библиотека docling не полностью поддерживает кириллические шрифты
    
    Args:
        text: исходный текст с возможными кодами /uniXXXX
        
    Returns:
        Текст с исправленными символами
        
    Example:
        >>> fix_unicode_codes("Раскрытие в рамках вы/uni043Fуска")
        'Раскрытие в рамках выпуска'
    """
    # Паттерн для поиска кодов типа /uni043F, /uni044F и т.д.
    pattern = r'/uni([0-9A-Fa-f]{4})'
    
    # Выполняем замену
    fixed_text = re.sub(pattern, decode_unicode_code, text)
    
    # Логируем, если были исправления
    count = len(re.findall(pattern, text))
    if count > 0:
        logger.debug(f"Исправлено {count} Unicode-кодов")
    
    return fixed_text

