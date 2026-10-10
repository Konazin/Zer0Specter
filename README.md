# ZeroSpecter

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/konazin/zer0specter)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive penetration testing toolkit for authorized security assessments. ZeroSpecter provides a collection of security tools designed for ethical hackers and security professionals.

## ⚠️ Disclaimer

**This tool is intended for authorized security assessments only. Unauthorized use of this software against systems you do not own or have explicit permission to test is illegal and unethical. The authors are not responsible for any misuse of this software.**

## Features

- **Password Generator**: Generate secure passwords with customizable options
- **IP Geolocation**: Locate IP addresses and gather geographical information
- **Port Scanner**: Scan for open ports on target systems
- **ZIP Cracker**: Crack password-protected ZIP files using dictionary attacks
- **Network Sniffer**: Capture and analyze network traffic
- **WiFi Attack Tools**: Wireless network security assessment tools

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/konazin/zer0specter.git
cd zer0specter
./scripts/install.sh
```

### Manual Installation

0. **System requirements for GUI version**:
   - Linux (Debian/Ubuntu): `sudo apt update && sudo apt install python3-tk`
   - Fedora/RHEL: `sudo dnf install python3-tkinter`
   - Arch: `sudo pacman -S tk`
   - Windows: Select the option `tcl/tk` on Python installer (or install the suitable packet)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/konazin/zer0specter.git
   cd zer0specter
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ZeroSpecter:**
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

After installation, open the interactive terminal interface with:

```bash
zer0specter tui
```

Direct commands and help remain available from Bash:

```bash
zer0specter --help
zer0specter port-scanner --target 127.0.0.1
```

### Available Commands

- `tui` - Open the interactive terminal interface
- `packet-sniffer` - Capture and display network packets
- `port-scanner` - Scan target ports
- `ip-geolocation` - Retrieve geolocation information
- `password-generator` - Generate random secure passwords
- `zip-cracker` - Test passwords against a protected ZIP file
- `wifi-deauth` - Send Wi-Fi deauthentication packets

### Examples

**Generate a password:**
```
zer0specter password-generator --numberchar 16 --punctuation y --numbers y
```

**Scan ports:**
```
zer0specter port-scanner --target 192.168.1.1 --start 1 --end 1000
```

**Crack a ZIP file:**
```
zer0specter zip-cracker --path encrypted.zip --wordlist wordlist.txt
```

## Development

### Setup Development Environment

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
# Linting
flake8 zer0specter/

# Type checking
mypy zer0specter/

# Code formatting
black zer0specter/
isort zer0specter/
```

### Project Structure

```
zer0specter/
├── cli.py              # Command line interface
├── gui/                # Graphical user interface (future)
├── modules/            # Security modules
│   ├── passwd_gen.py   # Password generator
│   ├── ip_geo.py       # IP geolocation
│   ├── port_scanner.py # Port scanner
│   ├── zip_cracker.py  # ZIP cracker
│   ├── sniffer.py      # Network sniffer
│   └── wifi_attack.py  # WiFi tools
└── utils/              # Utility functions
    ├── banner.py       # ASCII banner
    ├── logger.py       # Logging utilities
    └── validators.py   # Input validation
```

## Requirements

- Python 3.9+
- See `requirements.txt` for Python dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Konazin** - [GitHub](https://github.com/konazin) - [Portifolio](https://konazin.github.io/)

## Acknowledgments

- Built with Python and various security libraries
- Inspired by the need for ethical security testing tools
- Thanks to the open-source security community
