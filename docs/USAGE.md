# ZeroSpecter Usage Guide

## Getting Started

After installation, start ZeroSpecter with:

```bash
zer0specter
```

You'll see the welcome banner and available commands.

## Command Reference

### Core Commands

- `help` - Display help information and available commands
- `quit` or `exit` - Exit the program

### Module Commands

#### Password Generator (`passgen`)

Generate secure passwords with various options.

**Syntax:**
```
passgen [OPTIONS]
```

**Options:**
- `-l, --length LENGTH` - Password length (default: 12)
- `-s, --symbols` - Include symbols (!@#$%^&*)
- `-n, --numbers` - Include numbers (0-9)
- `-u, --uppercase` - Include uppercase letters
- `-c, --count COUNT` - Number of passwords to generate (default: 1)

**Examples:**
```bash
# Generate a 16-character password with all character types
passgen -l 16 -s -n -u

# Generate 5 passwords of default length
passgen -c 5
```

#### IP Locator (`iplocator`)

Get geographical information about an IP address.

**Syntax:**
```
iplocator <IP_ADDRESS>
```

**Examples:**
```bash
iplocator 8.8.8.8
iplocator 192.168.1.1
```

#### Port Scanner (`portscan`)

Scan for open ports on a target system.

**Syntax:**
```
portscan -t TARGET [OPTIONS]
```

**Options:**
- `-t, --target TARGET` - Target IP address or hostname (required)
- `-p, --ports PORTS` - Port range (default: 1-1024)
- `-T, --timeout TIMEOUT` - Timeout in seconds (default: 1)
- `-v, --verbose` - Verbose output

**Examples:**
```bash
# Scan common ports on localhost
portscan -t 127.0.0.1

# Scan ports 80-443 on a specific IP
portscan -t 192.168.1.100 -p 80-443

# Scan with longer timeout
portscan -t example.com -p 1-1000 -T 2
```

#### ZIP Cracker (`zipcrack`)

Crack password-protected ZIP files using dictionary attack.

**Syntax:**
```
zipcrack -f FILE -w WORDLIST [OPTIONS]
```

**Options:**
- `-f, --file FILE` - Path to ZIP file (required)
- `-w, --wordlist WORDLIST` - Path to wordlist file (required)
- `-v, --verbose` - Show cracking progress

**Examples:**
```bash
zipcrack -f secret.zip -w rockyou.txt
zipcrack -f encrypted.zip -w /path/to/wordlist.txt -v
```

#### Network Sniffer (`sniffer`)

Capture and analyze network traffic.

**Syntax:**
```
sniffer [OPTIONS]
```

**Options:**
- `-i, --interface INTERFACE` - Network interface to sniff on
- `-f, --filter FILTER` - BPF filter expression
- `-c, --count COUNT` - Number of packets to capture (default: unlimited)
- `-v, --verbose` - Verbose output

**Examples:**
```bash
# Sniff on default interface
sniffer

# Sniff HTTP traffic
sniffer -f "tcp port 80"

# Capture 100 packets on eth0
sniffer -i eth0 -c 100
```

#### WiFi Tools (`wifi`)

Wireless network security assessment tools.

**Syntax:**
```
wifi <SUBCOMMAND> [OPTIONS]
```

**Subcommands:**
- `scan` - Scan for wireless networks
- `monitor` - Enable monitor mode
- `deauth` - Send deauthentication packets

**Examples:**
```bash
# Scan for networks
wifi scan

# Enable monitor mode on wlan0
wifi monitor -i wlan0

# Send deauth packets (use with caution)
wifi deauth -b 00:11:22:33:44:55 -c 00:11:22:33:44:66
```

## Advanced Usage

### Command Line Arguments

You can also pass arguments directly when starting ZeroSpecter:

```bash
# Run a command directly
zer0specter -c "passgen -l 20 -s -n -u"

# Start in quiet mode
zer0specter -q
```

### Output Redirection

Capture output to files:

```bash
# Save password list to file
zer0specter -c "passgen -c 10" > passwords.txt

# Save scan results
zer0specter -c "portscan -t 192.168.1.1" > scan_results.txt
```

### Batch Operations

Use the `-c` flag for batch operations:

```bash
# Run multiple commands
zer0specter -c "passgen -c 5; portscan -t localhost; quit"
```

## Troubleshooting

### Common Issues

1. **Permission denied errors:**
   - Some tools require root/administrator privileges
   - Run with `sudo` if necessary

2. **Network interface not found:**
   - Check available interfaces with `ifconfig` or `ip addr`
   - Use the correct interface name

3. **Module import errors:**
   - Ensure all dependencies are installed
   - Check Python version compatibility

4. **Virtual environment issues:**
   - Always activate the virtual environment before running
   - Reinstall if environment is corrupted

### Getting Help

- Use `help` command within ZeroSpecter
- Check the main README.md for installation instructions
- Report issues on GitHub

## Security Notes

- Always use this tool responsibly and legally
- Obtain proper authorization before testing any systems
- Be aware of local laws regarding security testing
- Some features may require special permissions or hardware
