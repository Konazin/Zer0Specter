"""ZeroSpecter - A comprehensive penetration testing toolkit."""

__version__ = "2.1.2"
__author__ = "Konazin"
__description__ = "A comprehensive penetration testing toolkit for authorized security assessments"
__license__ = "MIT"

# Import main components for easy access
try:
    from .cli import main
    from .utils.logger import setup_logger, get_logger
    from .utils.banner import show_banner
except ImportError:
    # Handle import errors gracefully during development
    pass

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "__license__",
    "main",
    "setup_logger",
    "get_logger",
    "show_banner",
]