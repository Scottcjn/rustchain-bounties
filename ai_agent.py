import os
import sys
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

class AIAgent:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
        self.error_translations = {
            'en': {
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'success': 'Success',
                'unknown_error': 'Unknown error occurred',
                'file_not_found': 'File not found',
                'permission_denied': 'Permission denied',
                'invalid_input': 'Invalid input',
                'connection_failed': 'Connection failed',
                'timeout': 'Operation timed out'
            },
            'es': {
                'error': 'Error',
                'warning': 'Advertencia',
                'info': 'Información',
                'success': 'Éxito',
                'unknown_error': 'Ocurrió un error desconocido',
                'file_not_found': 'Archivo no encontrado',
                'permission_denied': 'Permiso denegado',
                'invalid_input': 'Entrada inválida',
                'connection_failed': 'Falló la conexión',
                'timeout': 'Operación agotó el tiempo de espera'
            },
            'fr': {
                'error': 'Erreur',
                'warning': 'Avertissement',
                'info': 'Information',
                'success': 'Succès',
                'unknown_error': 'Une erreur inconnue s\'est produite',
                'file_not_found': 'Fichier non trouvé',
                'permission_denied': 'Permission refusée',
                'invalid_input': 'Entrée invalide',
                'connection_failed': 'Échec de la connexion',
                'timeout': 'Opération expirée'
            },
            'de': {
                'error': 'Fehler',
                'warning': 'Warnung',
                'info': 'Information',
                'success': 'Erfolg',
                'unknown_error': 'Ein unbekannter Fehler ist aufgetreten',
                'file_not_found': 'Datei nicht gefunden',
                'permission_denied': 'Berechtigung verweigert',
                'invalid_input': 'Ungültige Eingabe',
                'connection_failed': 'Verbindung fehlgeschlagen',
                'timeout': 'Vorgang abgelaufen'
            },
            'it': {
                'error': 'Errore',
                'warning': 'Avvertimento',
                'info': 'Informazione',
                'success': 'Successo',
                'unknown_error': 'Si è verificato un errore sconosciuto',
                'file_not_found': 'File non trovato',
                'permission_denied': 'Permesso negato',
                'invalid_input': 'Input non valido',
                'connection_failed': 'Connessione fallita',
                'timeout': 'Operazione scaduta'
            },
            'pt': {
                'error': 'Erro',
                'warning': 'Aviso',
                'info': 'Informação',
                'success': 'Sucesso',
                'unknown_error': 'Ocorreu um erro desconhecido',
                'file_not_found': 'Arquivo não encontrado',
                'permission_denied': 'Permissão negada',
                'invalid_input': 'Entrada inválida',
                'connection_failed': 'Falha na conexão',
                'timeout': 'Operação expirou'
            },
            'ru': {
                'error': 'Ошибка',
                'warning': 'Предупреждение',
                'info': 'Информация',
                'success': 'Успех',
                'unknown_error': 'Произошла неизвестная ошибка',
                'file_not_found': 'Файл не найден',
                'permission_denied': 'Отказано в доступе',
                'invalid_input': 'Неверный ввод',
                'connection_failed': 'Ошибка подключения',
                'timeout': 'Операция завершена по таймауту'
            },
            'ja': {
                'error': 'エラー',
                'warning': '警告',
                'info': '情報',
                'success': '成功',
                'unknown_error': '不明なエラーが発生しました',
                'file_not_found': 'ファイルが見つかりません',
                'permission_denied': 'アクセスが拒否されました',
                'invalid_input': '無効な入力',
                'connection_failed': '接続に失敗しました',
                'timeout': '操作がタイムアウトしました'
            },
            'ko': {
                'error': '오류',
                'warning': '경고',
                'info': '정보',
                'success': '성공',
                'unknown_error': '알 수 없는 오류가 발생했습니다',
                'file_not_found': '파일을 찾을 수 없습니다',
                'permission_denied': '권한이 거부되었습니다',
                'invalid_input': '잘못된 입력',
                'connection_failed': '연결에 실패했습니다',
                'timeout': '작업이 시간 초과되었습니다'
            },
            'zh': {
                'error': '错误',
                'warning': '警告',
                'info': '信息',
                'success': '成功',
                'unknown_error': '发生未知错误',
                'file_not_found': '文件未找到',
                'permission_denied': '权限被拒绝',
                'invalid_input': '无效输入',
                'connection_failed': '连接失败',
                'timeout': '操作超时'
            },
            'ar': {
                'error': 'خطأ',
                'warning': 'تحذير',
                'info': 'معلومات',
                'success': 'نجاح',
                'unknown_error': 'حدث خطأ غير معروف',
                'file_not_found': 'الملف غير موجود',
                'permission_denied': 'تم رفض الإذن',
                'invalid_input': 'مدخل غير صالح',
                'connection_failed': 'فشل الاتصال',
                'timeout': 'انتهت مهلة العملية'
            }
        }
        
    def detect_language(self, text: str) -> str:
        """Simple language detection based on text analysis"""
        # This is a simplified implementation
        # In a real-world scenario, you would use a proper language detection library
        
        # Check for common language patterns
        if any(char in text for char in ['é', 'è', 'ê', 'ë', 'à', 'â', 'ä', 'ô', 'ö', 'û', 'ü', 'ç', 'ñ']):
            return 'fr'
        elif any(char in text for char in ['ñ', 'ü', 'ß', 'ä', 'ö', 'ü']):
            return 'de'
        elif any(char in text for char in ['ñ', 'á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ']):
            return 'es'
        elif any(char in text for char in ['à', 'è', 'ì', 'ò', 'ù', 'é', 'ò', 'ç']):
            return 'it'
        elif any(char in text for char in ['ã', 'õ', 'á', 'é', 'í', 'ó', 'ú', 'ç']):
            return 'pt'
        elif any(char in text for char in ['я', 'ю', 'э', 'ь', 'ы', 'ъ', 'ё']):
            return 'ru'
        elif any(char in text for char in ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ']):
            return 'ja'
        elif any(char in text for char in ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차']):
            return 'ko'
        elif any(char in text for char in ['中', '国', '人', '大', '小', '上', '下', '左', '右']):
            return 'zh'
        elif any(char in text for char in ['أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر']):
            return 'ar'
        else:
            return 'en'  # Default to English
    
    def translate_error(self, error_message: str, target_language: Optional[str] = None) -> str:
        """Translate an error message to the target language"""
        if target_language is None:
            # Auto-detect the language of the error message
            target_language = self.detect_language(error_message)
        
        # Get the error key (simplified - in reality you'd need proper error classification)
        error_key = self.classify_error(error_message)
        
        # Get the translation if available
        if target_language in self.error_translations and error_key in self.error_translations[target_language]:
            translated = self.error_translations[target_language][error_key]
            return f"[{target_language.upper()}] {translated}: {error_message}"
        else:
            # Fallback to English if translation not available
            if 'en' in self.error_translations and error_key in self.error_translations['en']:
                translated = self.error_translations['en'][error_key]
                return f"[{target_language.upper()}] {translated}: {error_message}"
            else:
                return f"[{target_language.upper()}] Unknown error: {error_message}"
    
    def classify_error(self, error_message: str) -> str:
        """Classify the error message to get the appropriate translation key"""
        error_lower = error_message.lower()
        
        if 'file' in error_lower and 'not found' in error_lower:
            return 'file_not_found'
        elif 'permission' in error_lower and 'denied' in error_lower:
            return 'permission_denied'
        elif 'invalid' in error_lower and 'input' in error_lower:
            return 'invalid_input'
        elif 'connection' in error_lower and 'failed' in error_lower:
            return 'connection_failed'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'error' in error_lower:
            return 'error'
        elif 'warning' in error_lower:
            return 'warning'
        elif 'info' in error_lower:
            return 'info'
        elif 'success' in error_lower:
            return 'success'
        else:
            return 'unknown_error'
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get the list of supported languages"""
        return self.supported_languages
    
    def add_language_support(self, language_code: str, language_name: str, translations: Dict[str, str]) -> bool:
        """Add support for a new language"""
        if language_code in self.supported_languages:
            return False
        
        self.supported_languages[language_code] = language_name
        self.error_translations[language_code] = translations
        return True
    
    def process_error(self, error_message: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Process an error message and return translation information"""
        detected_language = self.detect_language(error_message) if language is None else language
        translated_message = self.translate_error(error_message, detected_language)
        
        return {
            'original_message': error_message,
            'detected_language': detected_language,
            'translated_message': translated_message,
            'error_type': self.classify_error(error_message),
            'supported_languages': list(self.supported_languages.keys())
        }


# Example usage
if __name__ == "__main__":
    agent = AIAgent()
    
    # Test with different error messages
    test_errors = [
        "File not found: example.txt",
        "Permission denied when accessing /etc/passwd",
        "Invalid input: expected number but got string",
        "Connection failed: could not reach server",
        "Operation timed out after 30 seconds",
        "Unknown error occurred while processing request"
    ]
    
    for error in test_errors:
        result = agent.process_error(error)
        print(f"Original: {result['original_message']}")
        print(f"Detected Language: {result['detected_language']}")
        print(f"Translated: {result['translated_message']}")
        print(f"Error Type: {result['error_type']}")
        print("-" * 50)
    
    # Test with specific language
    print("\nTesting with specific language (Spanish):")
    result = agent.process_error("File not found: example.txt", "es")
    print(f"Original: {result['original_message']}")
    print(f"Translated: {result['translated_message']}")
    print("-" * 50)
