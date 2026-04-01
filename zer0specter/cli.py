import os
import time
import platform
import sys
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


match(platform.system()):
    case "Linux":
        import readline
    case "Windows":
        from pyreadline3 import Readline

try:
    from zer0specter.modules.zip_cracker import zipcrack
    from zer0specter.modules.ip_geo import ip_locator
    from zer0specter.modules.passwd_gen import password_generator
    from zer0specter.modules.port_scanner import portscanner
    from zer0specter.modules.sniffer import sniffer
    from zer0specter.modules.wifi_attack import wifi_attack
    from zer0specter.utils.banner import show_banner
except ImportError as error:
    print(f"[#] Error importing modules: {error}")
    quit()


FEATURES = {
    "zipcrack": (zipcrack, "Crack password-protected ZIP files"),
    "passgen": (password_generator, "Generate random secure passwords"),
    "wifiattack": (wifi_attack, "Perform Wi-Fi deauthentication (DoS) attacks"),
    "iplocator": (ip_locator, "Geolocate an IP address"),
    "sniffer": (sniffer, "Capture and display network packets"),
    "portscanner": (portscanner, "Check open ports by bruteforce"),
}

def main():
    """Main entry point for ZeroSpecter CLI."""
    show_banner()
    terminal()

def show_help():
    print("\nAvailable commands:")
    for cmd, (_, desc) in FEATURES.items():
        print(f"  {cmd:<15} {desc}")
    print("  help            Show this help message")
    print("  quit / exit     Exit the program\n")

def terminal():
    while True:
        try:
            user_input = input("[Zer0Specter] > ").strip()
            if not user_input:
                continue
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in FEATURES:
                try:
                    if command == "gui":
                        # Executar GUI em thread separada (não-bloqueante)
                        gui_thread = threading.Thread(target=FEATURES[command][0], args=(args,), daemon=True)
                        gui_thread.start()
                        print("[INFO] GUI iniciada em thread separado. CLI continua disponível.\n")
                    else:
                        FEATURES[command][0](args)
                except SystemExit:
                    pass  
                except Exception as e:
                    print(f"[ERROR] An unexpected error occurred: {e}")
            elif command in ["quit", "exit"]:
                print("Exiting...")
                time.sleep(1)
                break
            elif command == "clear":
                os.system("clear" if os.name != "nt" else "cls")
            elif command == "help":
                show_help()
            else:
                print(f"[ERROR] Unknown command: '{command}'. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
if __name__=="__main__":
    main()