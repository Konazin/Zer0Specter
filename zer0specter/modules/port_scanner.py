"""TCP port scanner with an optional banner probe."""

import argparse
import math
import socket
from typing import List, Optional, Tuple

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import (
    validate_ip_address,
    validate_port_range,
    validate_timeout,
)


def _scan_port(
    host: str, port: int, timeout: float, probe_banner: bool
) -> Tuple[bool, Optional[str]]:
    """Return TCP reachability separately from any banner text."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout)
        try:
            connection.connect((host, port))
        except PermissionError:
            raise
        except OSError:
            return False, None

        if not probe_banner:
            return True, None

        try:
            data = connection.recv(1024)
            if not data:
                connection.sendall(
                    b"HEAD / HTTP/1.0\r\nHost: " + host.encode("ascii") + b"\r\n\r\n"
                )
                data = connection.recv(2048)
            if not data:
                return True, None

            lines = data.decode("utf-8", errors="replace").splitlines()
            for line in lines:
                if line.lower().startswith("server:"):
                    return True, line.strip()
            return True, lines[0].strip() if lines else None
        except (OSError, TimeoutError):
            return True, None


def portscanner(argus: List[str]) -> int:
    """Scan a target and print open TCP ports to stdout."""
    parser = argparse.ArgumentParser(description="TCP port scanner")
    parser.add_argument(
        "-t", "--target", required=True, help="IPv4 address or hostname"
    )
    parser.add_argument("-s", "--start", type=int, default=1, help="first port")
    parser.add_argument("-e", "--end", type=int, default=2048, help="last port")
    parser.add_argument(
        "-d",
        "--delay",
        "--timeout",
        type=float,
        default=0.2,
        help="connection timeout in seconds",
    )
    parser.add_argument(
        "--banner", action="store_true", help="probe open ports for a banner"
    )
    args = parser.parse_args(argus)
    logger = get_logger()

    valid_range, port_range = validate_port_range(f"{args.start}-{args.end}")
    if not valid_range:
        parser.error("ports must be within 1..65535 and start must not exceed end")

    valid_timeout, timeout = validate_timeout(args.delay)
    if not valid_timeout or not math.isfinite(timeout):
        parser.error("timeout must be a finite positive number")

    if validate_ip_address(args.target):
        if ":" in args.target:
            parser.error("IPv6 targets are not supported")
        target = args.target
    else:
        try:
            target = socket.gethostbyname(args.target)
        except socket.gaierror:
            logger.error("Could not resolve target hostname")
            return 1

    start, end = port_range
    logger.info("Scanning %s TCP ports %s-%s", target, start, end)
    open_ports = []
    try:
        for port in range(start, end + 1):
            is_open, banner = _scan_port(target, port, timeout, args.banner)
            if is_open:
                open_ports.append((port, banner))
    except OSError as error:
        logger.error("Port scan failed (%s)", type(error).__name__)
        return 1

    if not open_ports:
        print("No open ports found.")
        return 0

    for port, banner in open_ports:
        line = f"{port}/tcp open"
        if banner:
            line += f" - {banner}"
        print(line)
    return 0
