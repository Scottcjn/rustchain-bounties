import json
import os
from typing import Dict, Optional, Any
import locale
import gettext
from pathlib import Path

class I18n:
    def __init__(self, default_language: str = 'en'):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.locales_dir = Path(__file__).parent / 'locales'
        self.locales_dir.mkdir(exist_ok=True)
        self._load_translations()
    
    def _detect_system_language(self) -> str:
        """Detect system language"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                return system_locale.split('_')[0].lower()
        except:
            pass
        return self.default_language
    
    def _load_translations(self):
        """Load all available translations"""
        for lang_file in self.locales_dir.glob('*.json'):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translation file {lang_file}: {e}")
    
    def set_language(self, language: str):
        """Set current language"""
        if language in self.translations or language == self.default_language:
            self.current_language = language
        else:
            print(f"Language {language} not available, using {self.default_language}")
            self.current_language = self.default_language
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        languages = list(self.translations.keys())
        if self.default_language not in languages:
            languages.append(self.default_language)
        return sorted(languages)
    
    def translate(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Translate a message key"""
        # Try current language first
        if self.current_language in self.translations:
            message = self.translations[self.current_language].get(key)
            if message:
                return self._format_message(message, **kwargs)
        
        # Fall back to default language
        if self.default_language in self.translations:
            message = self.translations[self.default_language].get(key)
            if message:
                return self._format_message(message, **kwargs)
        
        # Use default or key as fallback
        fallback = default or key
        return self._format_message(fallback, **kwargs)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with parameters"""
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    
    def add_translation(self, language: str, key: str, value: str):
        """Add a translation for a specific key"""
        if language not in self.translations:
            self.translations[language] = {}
        self.translations[language][key] = value
    
    def save_translations(self, language: str):
        """Save translations to file"""
        if language not in self.translations:
            return
        
        lang_file = self.locales_dir / f'{language}.json'
        try:
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[language], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving translation file {lang_file}: {e}")
    
    def load_from_po(self, language: str, po_file: str):
        """Load translations from gettext PO file"""
        try:
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            translations = {}
            lines = content.split('\n')
            msgid = None
            msgstr = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('msgid "'):
                    msgid = line[7:-1]
                elif line.startswith('msgstr "'):
                    msgstr = line[8:-1]
                    if msgid and msgstr:
                        translations[msgid] = msgstr
                    msgid = None
                    msgstr = None
            
            self.translations[language] = translations
            
        except Exception as e:
            print(f"Error loading PO file {po_file}: {e}")

# Global instance
i18n = I18n()

# Convenience functions
def _(key: str, default: Optional[str] = None, **kwargs) -> str:
    """Translate function (shorthand)"""
    return i18n.translate(key, default, **kwargs)

def set_language(language: str):
    """Set current language"""
    i18n.set_language(language)

def get_language() -> str:
    """Get current language"""
    return i18n.current_language

def detect_language() -> str:
    """Detect system language"""
    return i18n._detect_system_language()

# Common error messages
ERROR_MESSAGES = {
    'en': {
        'connection_failed': 'Connection failed: {error}',
        'invalid_credentials': 'Invalid username or password',
        'permission_denied': 'Permission denied',
        'file_not_found': 'File not found: {filename}',
        'network_error': 'Network error occurred',
        'timeout_error': 'Request timed out',
        'invalid_input': 'Invalid input: {input}',
        'server_error': 'Internal server error',
        'validation_error': 'Validation failed: {details}',
        'unknown_error': 'An unknown error occurred'
    }
}

# Load default error messages
for lang, messages in ERROR_MESSAGES.items():
    for key, value in messages.items():
        i18n.add_translation(lang, key, value)