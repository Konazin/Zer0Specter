"""GUI components for ZeroSpecter."""

try:
    from .app import launch
    __all__ = ["launch"]
except ImportError:
    # GUI dependencies not available
    __all__ = []
