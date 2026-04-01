"""Input validation utilities for ZeroSpecter."""

import ipaddress
import os
import re
from typing import Union, Tuple, Optional
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_ip_address(ip: str) -> bool:
    """
    Validate if a string is a valid IP address (IPv4 or IPv6).

    Args:
        ip: IP address string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ip_network(network: str) -> bool:
    """
    Validate if a string is a valid IP network (CIDR notation).

    Args:
        network: Network string in CIDR notation

    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_network(network, strict=False)
        return True
    except ValueError:
        return False


def validate_port(port: Union[str, int]) -> Tuple[bool, Optional[int]]:
    """
    Validate if a value is a valid port number.

    Args:
        port: Port number to validate

    Returns:
        Tuple of (is_valid, port_number)
    """
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return True, port_num
        return False, None
    except (ValueError, TypeError):
        return False, None


def validate_port_range(port_range: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    Validate if a string represents a valid port range (e.g., "80-443").

    Args:
        port_range: Port range string

    Returns:
        Tuple of (is_valid, (start_port, end_port))
    """
    if not port_range or '-' not in port_range:
        return False, None

    try:
        start_str, end_str = port_range.split('-', 1)
        start_valid, start_port = validate_port(start_str.strip())
        end_valid, end_port = validate_port(end_str.strip())

        if not (start_valid and end_valid):
            return False, None

        if start_port > end_port:
            return False, None

        return True, (start_port, end_port)
    except ValueError:
        return False, None


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate if a path is a valid file path.

    Args:
        file_path: File path to validate
        must_exist: Whether the file must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(file_path)

        # Check for invalid characters in path
        if '\x00' in str(path):
            return False, "Path contains null characters"

        # Check if path is absolute or relative
        if not path.is_absolute() and not str(path).startswith('.'):
            # Convert to absolute path for validation
            path = path.resolve()

        # Check if file exists (if required)
        if must_exist and not path.exists():
            return False, f"File does not exist: {path}"

        if must_exist and path.exists() and not path.is_file():
            return False, f"Path is not a file: {path}"

        # Check if we have read permission
        if must_exist and path.exists():
            try:
                with open(path, 'rb') as f:
                    f.read(1)
            except PermissionError:
                return False, f"No read permission for file: {path}"

        return True, None

    except (OSError, ValueError) as e:
        return False, f"Invalid file path: {e}"


def validate_directory_path(dir_path: Union[str, Path], must_exist: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate if a path is a valid directory path.

    Args:
        dir_path: Directory path to validate
        must_exist: Whether the directory must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(dir_path)

        # Check for invalid characters
        if '\x00' in str(path):
            return False, "Path contains null characters"

        if must_exist and not path.exists():
            return False, f"Directory does not exist: {path}"

        if must_exist and path.exists() and not path.is_dir():
            return False, f"Path is not a directory: {path}"

        return True, None

    except (OSError, ValueError) as e:
        return False, f"Invalid directory path: {e}"


def validate_domain_name(domain: str) -> bool:
    """
    Validate if a string is a valid domain name.

    Args:
        domain: Domain name to validate

    Returns:
        True if valid, False otherwise
    """
    if not domain or len(domain) > 253:
        return False

    # Remove trailing dot
    if domain.endswith('.'):
        domain = domain[:-1]

    # Check each label
    labels = domain.split('.')
    if len(labels) < 2:
        return False

    for label in labels:
        if not label or len(label) > 63:
            return False
        # Check valid characters and format
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', label):
            return False

    return True


def validate_mac_address(mac: str) -> bool:
    """
    Validate if a string is a valid MAC address.

    Args:
        mac: MAC address to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove separators and convert to lowercase
    mac = re.sub(r'[:-]', '', mac).lower()

    # Check length (12 hex characters)
    if len(mac) != 12:
        return False

    # Check if all characters are valid hex
    try:
        int(mac, 16)
        return True
    except ValueError:
        return False


def validate_password_length(length: Union[str, int]) -> Tuple[bool, Optional[int]]:
    """
    Validate password length parameter.

    Args:
        length: Password length to validate

    Returns:
        Tuple of (is_valid, length_number)
    """
    try:
        length_num = int(length)
        if 1 <= length_num <= 1000:  # Reasonable upper limit
            return True, length_num
        return False, None
    except (ValueError, TypeError):
        return False, None


def validate_timeout(timeout: Union[str, int, float]) -> Tuple[bool, Optional[float]]:
    """
    Validate timeout parameter.

    Args:
        timeout: Timeout value to validate

    Returns:
        Tuple of (is_valid, timeout_number)
    """
    try:
        timeout_num = float(timeout)
        if timeout_num > 0:
            return True, timeout_num
        return False, None
    except (ValueError, TypeError):
        return False, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

    # Trim whitespace and dots
    filename = filename.strip(' .')

    # Ensure not empty
    if not filename:
        filename = "unnamed_file"

    return filename


def validate_input_range(value: Union[str, int], min_val: int, max_val: int) -> Tuple[bool, Optional[int]]:
    """
    Validate if a value is within a specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (is_valid, value_number)
    """
    try:
        val_num = int(value)
        if min_val <= val_num <= max_val:
            return True, val_num
        return False, None
    except (ValueError, TypeError):
        return False, None
