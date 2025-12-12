"""Internationalization utilities"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Supported languages
SUPPORTED_LANGUAGES = {"ru", "en"}

# Cache for translations
_translations_cache: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)


def load_translations(language: str = "ru") -> Dict[str, Any]:
    """Load translations for specified language"""
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language '{language}', falling back to 'ru'")
        language = "ru"

    if language in _translations_cache:
        return _translations_cache[language]

    locales_path = Path(__file__).parent.parent / "locales"
    locale_file = locales_path / f"{language}.json"

    if not locale_file.exists():
        # Fallback to Russian if language file doesn't exist
        if language != "ru":
            logger.warning(f"Translation file for '{language}' not found, falling back to 'ru'")
            return load_translations("ru")
        # If Russian also doesn't exist, return empty dict
        logger.error("Russian translation file not found, returning empty translations")
        return {}

    try:
        with open(locale_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
            # Validate basic structure
            if not isinstance(translations, dict) or "ui" not in translations:
                raise ValueError("Invalid translation file structure")

            _translations_cache[language] = translations
            logger.debug(f"Loaded translations for language '{language}'")
            return translations
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in translation file {locale_file}: {e}")
    except Exception as e:
        logger.error(f"Error loading translations for '{language}': {e}")

    # Fallback on any error
    if language != "ru":
        return load_translations("ru")
    return {}


def get_translation(key: str, language: str = "ru", default: str = None) -> str:
    """Get translation for a key"""
    translations = load_translations(language)

    # Navigate through nested keys (e.g., "ui.title")
    keys = key.split(".")
    value = translations

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default if default is not None else key

    return value if isinstance(value, str) else (default if default is not None else key)


def get_all_translations(language: str = "ru") -> Dict[str, Any]:
    """Get all translations for a language"""
    return load_translations(language)


def get_supported_languages() -> set:
    """Get set of supported languages"""
    return SUPPORTED_LANGUAGES.copy()


def clear_cache() -> None:
    """Clear translations cache (useful for development)"""
    global _translations_cache
    _translations_cache.clear()
    logger.info("Translations cache cleared")

