"""Capture and display packets from a network interface."""

import argparse
import time
from typing import List

from zer0specter.utils.logger import get_logger


def sniffer(argus: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Packet sniffer (like tcpdump)")
    parser.add_argument(
        "-i", "--interface", dest="interface", help="interface to capture"
    )
    parser.add_argument(
        "-si",
        "--showinterfaces",
        dest="show_interfaces",
        action="store_true",
        help="list available network interfaces",
    )
    args = parser.parse_args(argus)
    logger = get_logger()

    if args.show_interfaces:
        try:
            from scapy.all import ifaces
        except Exception as error:
            logger.error("Could not load network interfaces (%s)", type(error).__name__)
            return 1

        print("Available network interfaces:")
        for index, interface in enumerate(ifaces):
            print(f"{index}: {interface}")
        return 0

    if not args.interface:
        parser.error("specify an interface with -i/--interface")

    try:
        from scapy.all import ARP, Dot11, Ether, ICMP, IP, TCP, UDP, sniff
    except Exception as error:
        logger.error("Could not load packet capture support (%s)", type(error).__name__)
        return 1

    logger.info(
        "Capturing packets on interface %s; press Ctrl+C to stop", args.interface
    )
    print(f"{'TIME':<10} {'PROTOCOL':<8} {'SOURCE':<22} {'DESTINATION':<22} INFO")
    print("-" * 80)

    def process_packet(packet):
        try:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            protocol = "OTHER"
            source = destination = "N/A"
            info = ""

            if packet.haslayer(IP):
                source = packet[IP].src
                destination = packet[IP].dst
                protocol_number = packet[IP].proto
                protocol = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(
                    protocol_number, f"IP({protocol_number})"
                )

                if packet.haslayer(TCP):
                    info = f"{packet[TCP].sport} → {packet[TCP].dport}"
                elif packet.haslayer(UDP):
                    info = f"{packet[UDP].sport} → {packet[UDP].dport}"
                elif packet.haslayer(ICMP):
                    info = f"Type {packet[ICMP].type} Code {packet[ICMP].code}"
            elif packet.haslayer(ARP):
                protocol = "ARP"
                source = packet[ARP].psrc
                destination = packet[ARP].pdst
                info = "who-has" if packet[ARP].op == 1 else "is-at"
            elif packet.haslayer(Dot11):
                protocol = "WLAN"
                source = packet[Dot11].addr2 or "N/A"
                destination = packet[Dot11].addr1 or "N/A"
            else:
                if packet.haslayer(Ether):
                    source = packet[Ether].src
                    destination = packet[Ether].dst
                info = f"{len(packet)} bytes"

            source = str(source)
            destination = str(destination)
            source = source[:20] + ".." if len(source) > 20 else source
            destination = (
                destination[:20] + ".." if len(destination) > 20 else destination
            )
            info = str(info)
            info = info[:30] + ".." if len(info) > 30 else info
            print(
                f"{timestamp:<10} {protocol:<8} {source:<22} "
                f"{destination:<22} {info}"
            )
        except Exception as error:
            logger.debug("Could not format captured packet (%s)", type(error).__name__)

    try:
        sniff(iface=args.interface, prn=process_packet, store=False)
    except PermissionError:
        logger.error("Permission denied while capturing on %s", args.interface)
        return 1
    except KeyboardInterrupt:
        logger.warning("Packet capture interrupted by user")
        return 130
    except Exception as error:
        logger.error("Packet capture failed (%s)", type(error).__name__)
        return 1
    return 0
