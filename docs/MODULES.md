# ZeroSpecter Modules

This document describes each module in the ZeroSpecter toolkit, including their functionality, dependencies, and usage.

## Core Modules

### Password Generator (`passwd_gen.py`)

**Purpose:** Generate secure passwords with customizable options.

**Features:**
- Configurable password length
- Character set selection (lowercase, uppercase, numbers, symbols)
- Batch password generation
- Cryptographically secure random generation

**Dependencies:**
- `secrets` (built-in)
- `string` (built-in)
- `argparse` (built-in)

**API:**
```python
from zer0specter.modules.passwd_gen import generate_password

password = generate_password(length=16, use_symbols=True, use_numbers=True, use_uppercase=True)
```

### IP Geolocation (`ip_geo.py`)

**Purpose:** Retrieve geographical and network information about IP addresses.

**Features:**
- IP address validation
- Geolocation data (country, city, coordinates)
- Network information (ISP, organization)
- JSON output formatting

**Dependencies:**
- `requests`
- `json` (built-in)
- `ipaddress` (built-in)

**API:**
```python
from zer0specter.modules.ip_geo import get_ip_info

info = get_ip_info("8.8.8.8")
print(info['country'], info['city'])
```

### Port Scanner (`port_scanner.py`)

**Purpose:** Scan target systems for open network ports.

**Features:**
- TCP port scanning
- Configurable port ranges
- Timeout configuration
- Service detection
- Multi-threaded scanning

**Dependencies:**
- `socket` (built-in)
- `threading` (built-in)
- `concurrent.futures` (built-in)

**API:**
```python
from zer0specter.modules.port_scanner import scan_ports

open_ports = scan_ports("192.168.1.1", start_port=1, end_port=1024, timeout=1)
for port in open_ports:
    print(f"Port {port} is open")
```

### ZIP Cracker (`zip_cracker.py`)

**Purpose:** Crack password-protected ZIP files using dictionary attacks.

**Features:**
- Dictionary-based password cracking
- Progress reporting
- Support for various ZIP formats
- Error handling for corrupted files

**Dependencies:**
- `zipfile` (built-in)
- `pyzipper`
- `pycryptodomex`

**API:**
```python
from zer0specter.modules.zip_cracker import crack_zip

success, password = crack_zip("encrypted.zip", "wordlist.txt")
if success:
    print(f"Password found: {password}")
```

### Network Sniffer (`sniffer.py`)

**Purpose:** Capture and analyze network traffic.

**Features:**
- Packet capture using Scapy
- BPF filter support
- Real-time packet analysis
- Protocol detection
- Packet statistics

**Dependencies:**
- `scapy`
- `datetime` (built-in)
- `collections` (built-in)

**API:**
```python
from zer0specter.modules.sniffer import start_sniffing

# Sniff on interface with filter
packets = start_sniffing(interface="eth0", filter="tcp port 80", count=100)
for packet in packets:
    print(packet.summary())
```

### WiFi Attack Tools (`wifi_attack.py`)

**Purpose:** Wireless network security assessment tools.

**Features:**
- Network scanning
- Monitor mode management
- Deauthentication attacks
- WPS testing
- Signal strength monitoring

**Dependencies:**
- `scapy`
- `subprocess` (built-in)
- `re` (built-in)

**API:**
```python
from zer0specter.modules.wifi_attack import scan_networks

networks = scan_networks()
for network in networks:
    print(f"SSID: {network['ssid']}, BSSID: {network['bssid']}")
```

## Utility Modules

### Banner (`banner.py`)

**Purpose:** Display ASCII art banner and system information.

**Features:**
- Colorized ASCII banner
- Version information
- System status checks
- Module loading verification

**Dependencies:**
- `rich`

### Logger (`logger.py`)

**Purpose:** Centralized logging system for the toolkit.

**Features:**
- Multiple log levels
- File and console output
- Timestamp formatting
- Log rotation

**Dependencies:**
- `logging` (built-in)
- `datetime` (built-in)

### Validators (`validators.py`)

**Purpose:** Input validation and sanitization utilities.

**Features:**
- IP address validation
- Port range validation
- File path validation
- Input sanitization

**Dependencies:**
- `ipaddress` (built-in)
- `os` (built-in)
- `re` (built-in)

## Module Architecture

All modules follow a consistent architecture:

1. **Argument Parsing:** Use `argparse` for command-line options
2. **Error Handling:** Comprehensive exception handling with user-friendly messages
3. **Output Formatting:** Consistent output using Rich library
4. **Threading Safety:** Thread-safe operations where applicable
5. **Resource Management:** Proper cleanup of resources

### Module Interface

Each module implements a standard interface:

```python
def main():
    """Main entry point for the module."""
    parser = argparse.ArgumentParser(description="Module description")
    # Add arguments...
    args = parser.parse_args()

    try:
        # Module logic here
        result = perform_operation(args)
        display_result(result)
    except Exception as e:
        logger.error(f"Module error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
```

## Dependencies Management

The toolkit uses a modular dependency system:

- **Core dependencies** in `requirements.txt`: Essential for CLI operation
- **Development dependencies** in `requirements-dev.txt`: Testing and development tools
- **Optional dependencies** in `pyproject.toml`: GUI and additional features

## Security Considerations

- All modules include input validation
- Network operations use timeouts to prevent hanging
- File operations include permission checks
- Sensitive data is handled securely
- Logging avoids exposing sensitive information

## Future Modules

Planned additions:
- Web application scanner
- Vulnerability assessment tools
- Wireless cracking tools
- Forensic analysis utilities
- Report generation system
