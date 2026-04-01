from scapy.all import *
from scapy.all import Dot11, sendp, ARP, IP, TCP, UDP, ICMP, Ether

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
            pass

    try:
        sniff(iface=args_parsed.interface, prn=process_packet, store=False)
    except PermissionError:
        print("\n[!] Permission denied. Please run as root/Administrator.")
    except KeyboardInterrupt:
        print("\n\n[+] Sniffer stopped by user.")