"""Direct command-line entry point for ZeroSpecter."""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zer0specter.utils.logger import get_logger

FEATURES = {
    "packet-sniffer": (
        "zer0specter.modules.sniffer",
        "sniffer",
        "Capture and display network packets",
    ),
    "port-scanner": (
        "zer0specter.modules.port_scanner",
        "portscanner",
        "Scan target ports",
    ),
    "ip-geolocation": (
        "zer0specter.modules.ip_geo",
        "ip_locator",
        "Retrieve geolocation information for an IP address",
    ),
    "password-generator": (
        "zer0specter.modules.passwd_gen",
        "password_generator",
        "Generate random secure passwords",
    ),
    "zip-cracker": (
        "zer0specter.modules.zip_cracker",
        "zipcrack",
        "Test passwords against a protected ZIP file",
    ),
    "wifi-deauth": (
        "zer0specter.modules.wifi_attack",
        "wifi_attack",
        "Send Wi-Fi deauthentication packets",
    ),
}

ALIASES = {
    "sniffer": "packet-sniffer",
    "ports": "port-scanner",
    "geo": "ip-geolocation",
    "pass": "password-generator",
    "zip": "zip-cracker",
    "deauth": "wifi-deauth",
}


def show_help() -> None:
    """Print top-level commands and their aliases."""
    print("Usage: zer0specter <command> [options]\n")
    print("  -h, --help           Show this help message")
    print("Commands:")
    for command, (_, _, description) in FEATURES.items():
        aliases = [alias for alias, target in ALIASES.items() if target == command]
        alias_text = ", ".join(aliases)
        print(f"  {command:<21} {alias_text:<11} {description}")
    print(f"  {'tui':<21} {'':<11} Open the interactive terminal interface")
    print("\nUse 'zer0specter <command> --help' for command options.")


def _launch_tui() -> int:
    """Load Textual only when the user explicitly asks to open the TUI."""
    from zer0specter.tui import launch

    return launch()


def _load_feature(command: str):
    module_name, function_name, _ = FEATURES[command]
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def main() -> int:
    """Dispatch one command from the process arguments."""
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        show_help()
        return 0

    requested_command = argv[0]
    if requested_command == "tui":
        if len(argv) > 1:
            if len(argv) == 2 and argv[1] in ("-h", "--help"):
                print("Usage: zer0specter tui")
                return 0
            print("Usage: zer0specter tui", file=sys.stderr)
            return 2
        return _launch_tui()

    command = ALIASES.get(requested_command, requested_command)
    logger = get_logger()

    if command not in FEATURES:
        print(f"[ERROR] Unknown command: {requested_command!r}", file=sys.stderr)
        logger.warning("Rejected unknown command")
        show_help()
        return 2

    logger.info("Starting command: %s", command)
    try:
        result = _load_feature(command)(argv[1:])
        status = result if isinstance(result, int) else 0
    except SystemExit as error:
        if error.code is None:
            status = 0
        elif isinstance(error.code, int):
            status = error.code
        else:
            print(str(error.code), file=sys.stderr)
            status = 1
        logger.info("Command %s finished with status %s", command, status)
        return status
    except KeyboardInterrupt:
        logger.warning("Command %s interrupted", command)
        print("\n[!] Interrupted by user.", file=sys.stderr)
        return 130
    except Exception as error:
        logger.error("Command %s failed (%s)", command, type(error).__name__)
        print(
            f"[ERROR] {command} failed: {type(error).__name__}",
            file=sys.stderr,
        )
        return 1

    logger.info("Command %s finished with status %s", command, status)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
