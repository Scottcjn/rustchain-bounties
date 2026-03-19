import logging
from typing import Optional, Dict, Any
from src.i18n import get_text

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message_key: str, **kwargs):
        self.message_key = message_key
        self.kwargs = kwargs
        super().__init__(get_text(message_key, **kwargs))

class NetworkError(Exception):
    """Custom exception for network-related errors"""
    def __init__(self, message_key: str, **kwargs):
        self.message_key = message_key
        self.kwargs = kwargs
        super().__init__(get_text(message_key, **kwargs))

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    def __init__(self, message_key: str, **kwargs):
        self.message_key = message_key
        self.kwargs = kwargs
        super().__init__(get_text(message_key, **kwargs))

class ErrorHandler:
    """Centralized error handling with internationalization support"""
    
    @staticmethod
    def handle_validation_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle validation errors and return localized message"""
        if isinstance(error, ValidationError):
            return str(error)
        
        logger.error(f"Validation error: {str(error)}")
        if context and 'field' in context:
            return get_text("error.validation.field", field=context['field'])
        return get_text("error.validation.general")
    
    @staticmethod
    def handle_network_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle network errors and return localized message"""
        if isinstance(error, NetworkError):
            return str(error)
        
        logger.error(f"Network error: {str(error)}")
        if "timeout" in str(error).lower():
            return get_text("error.network.timeout")
        elif "connection" in str(error).lower():
            return get_text("error.network.connection")
        return get_text("error.network.general")
    
    @staticmethod
    def handle_configuration_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle configuration errors and return localized message"""
        if isinstance(error, ConfigurationError):
            return str(error)
        
        logger.error(f"Configuration error: {str(error)}")
        if context and 'config_key' in context:
            return get_text("error.config.missing_key", key=context['config_key'])
        return get_text("error.config.general")
    
    @staticmethod
    def handle_file_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle file operation errors and return localized message"""
        logger.error(f"File error: {str(error)}")
        
        if "permission" in str(error).lower():
            return get_text("error.file.permission")
        elif "not found" in str(error).lower():
            filename = context.get('filename', '') if context else ''
            return get_text("error.file.not_found", filename=filename)
        elif "disk" in str(error).lower() or "space" in str(error).lower():
            return get_text("error.file.disk_space")
        return get_text("error.file.general")
    
    @staticmethod
    def handle_generic_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle generic errors and return localized message"""
        logger.error(f"Unexpected error: {str(error)}")
        return get_text("error.generic")
    
    @classmethod
    def handle_error(cls, error: Exception, error_type: Optional[str] = None, 
                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main error handling method that routes to appropriate handler
        
        Args:
            error: The exception that occurred
            error_type: Optional error type hint
            context: Optional context information
            
        Returns:
            Localized error message string
        """
        if error_type == "validation" or isinstance(error, ValidationError):
            return cls.handle_validation_error(error, context)
        elif error_type == "network" or isinstance(error, NetworkError):
            return cls.handle_network_error(error, context)
        elif error_type == "configuration" or isinstance(error, ConfigurationError):
            return cls.handle_configuration_error(error, context)
        elif error_type == "file":
            return cls.handle_file_error(error, context)
        else:
            return cls.handle_generic_error(error, context)

def safe_execute(func, *args, **kwargs):
    """
    Safely execute a function and return either result or error message
    
    Args:
        func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Tuple of (success: bool, result_or_error_message: Any)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        error_message = ErrorHandler.handle_error(e)
        return False, error_message