"""Small, Fusion-independent translation layer with English source messages.

Configure once when the add-in starts using Fusion's UI language. User data,
command IDs, units and preset schemas must never pass through this module.
"""

from functools import lru_cache
import json
from pathlib import Path
from string import Formatter

DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = ('en', 'de', 'fr', 'es', 'pl')
_LOCALES = Path(__file__).resolve().parent / 'locales'
_language = DEFAULT_LANGUAGE
_FUSION_LANGUAGES = {
    'EnglishLanguage': 'en',
    'GermanLanguage': 'de',
    'FrenchLanguage': 'fr',
    'SpanishLanguage': 'es',
    'PolishLanguage': 'pl',
}


def set_language(language):
    """Select a supported language code; unknown values use English."""
    global _language
    code = language.lower().replace('_', '-').split('-')[0] if isinstance(language, str) else ''
    _language = code if code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return _language


def get_language():
    return _language


def configure_from_fusion(app):
    """Read Fusion preferences without changing them or using the OS locale.

    Fusion applies language changes after restart. Enum members are looked up
    by name so older API versions can omit languages without breaking startup.
    Missing preferences/API access safely resets the language to English.
    """
    code = DEFAULT_LANGUAGE
    try:
        import adsk.core
        selected = app.preferences.generalPreferences.userLanguage
        for member, language in _FUSION_LANGUAGES.items():
            value = getattr(adsk.core.UserLanguages, member, None)
            if value is not None and selected == value:
                code = language
                break
    except (ImportError, AttributeError, RuntimeError, TypeError):
        pass
    return set_language(code)


def _fields(text):
    return sorted((field, spec, conversion) for _, field, spec, conversion
                  in Formatter().parse(text) if field is not None)


@lru_cache(maxsize=len(SUPPORTED_LANGUAGES))
def _catalog(language):
    if language == DEFAULT_LANGUAGE:
        return {}
    try:
        data = json.loads((_LOCALES / f'{language}.json').read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return {}
        valid = {}
        for source, translated in data.items():
            if not isinstance(translated, str) or not translated.strip():
                continue
            try:
                if _fields(source) == _fields(translated):
                    valid[source] = translated
            except ValueError:
                continue
        return valid
    except (OSError, ValueError):
        return {}


def tr(message, **values):
    """Translate a complete English message, then substitute named values.

    Missing catalogs/entries and invalid translation placeholders fall back to
    the English source message. Values (including names/paths) are not translated.
    """
    translated = _catalog(_language).get(message, message)
    return translated.format(**values) if values else translated
