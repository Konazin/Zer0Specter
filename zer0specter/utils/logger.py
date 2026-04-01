"""Logging utilities for ZeroSpecter."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class ZeroSpecterLogger:
    """Custom logger for ZeroSpecter with file and console output."""

    def __init__(self, name: str = "zer0specter", level: int = logging.INFO):
        self.name = name
        self.level = level
        self.logger = None
        self._setup_logger()

    def _setup_logger(self):
        """Setup the logger with console and file handlers."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )

        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "zer0specter.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

    def set_level(self, level: int):
        """Set the logging level."""
        self.level = level
        if self.logger:
            self.logger.setLevel(level)
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(level)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        if self.logger:
            self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        if self.logger:
            self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        if self.logger:
            self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        if self.logger:
            self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        if self.logger:
            self.logger.critical(message, *args, **kwargs)


# Global logger instance
_logger_instance: Optional[ZeroSpecterLogger] = None


def setup_logger(name: str = "zer0specter", level: int = logging.INFO) -> ZeroSpecterLogger:
    """Setup and return the global logger instance."""
    global _logger_instance
    _logger_instance = ZeroSpecterLogger(name, level)
    return _logger_instance


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = setup_logger()
    return _logger_instance.get_logger()


def log_function_call(func_name: str, args: tuple = None, kwargs: dict = None):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            arg_str = f"args={args}" if args else ""
            kwarg_str = f"kwargs={kwargs}" if kwargs else ""
            params = ", ".join(filter(None, [arg_str, kwarg_str]))
            logger.debug(f"Calling {func_name}({params})")

            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed: {e}")
                raise
        return wrapper
    return decorator
