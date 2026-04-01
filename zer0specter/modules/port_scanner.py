import argparse
import socket
import sys
from typing import List, Tuple, Optional

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import validate_ip_address, validate_port_range, validate_timeout

logger = get_logger()

def portscanner(argus: List[str]) -> None:
    """Port scanner module with banner grabbing capabilities."""

    def arguments() -> argparse.Namespace:
        """Parse command line arguments."""
        p = argparse.ArgumentParser(description="port scanner / banner grabber")
        p.add_argument("-t", "--target", help="IPv4 or hostname of target", dest="target", required=True)
        p.add_argument("-s", "--start", help="start port", dest="start", type=int, default=1)
        p.add_argument("-e", "--end", help="end port", dest="end", type=int, default=2048)
        p.add_argument("-d", "--delay", help="socket timeout in seconds", dest="timeout", type=float, default=0.2)
        return p.parse_args(argus)

    def scan(host: str, port: int, timeout: float) -> Optional[str]:
        """Scan a single port and attempt banner grabbing."""
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

    def scanner(host: str, start: int, end: int, timeout: float) -> None:
        """Perform port scanning on the specified range."""
        # Validate port range
        valid_range, port_tuple = validate_port_range(f"{start}-{end}")
        if not valid_range:
            logger.error("Invalid port range specified")
            return

        start, end = port_tuple

        open_ports: List[Tuple[int, str]] = []
        logger.info(f"Scanning {host} ports {start}..{end} (timeout={timeout}s)")

        for port in range(start, end + 1):
            banner = scan(host, port, timeout)
            if banner is not None:
                logger.info(f"OPEN {port:5d}  - banner: {banner}")
                open_ports.append((port, banner))

        if not open_ports:
            logger.info("NO OPEN PORTS FOUND")
        else:
            logger.info("Scan summary:")
            for port, banner in sorted(open_ports):
                logger.info(f" - {port:5d} : {banner}")

    def main() -> None:
        """Main function for port scanner."""
        args = arguments()

        # Validate target
        if not validate_ip_address(args.target):
            try:
                # Try to resolve hostname
                host_ip = socket.gethostbyname(args.target)
                logger.debug(f"Resolved {args.target} to {host_ip}")
            except socket.gaierror as e:
                logger.error(f"Could not resolve host '{args.target}': {e}")
                sys.exit(1)
        else:
            host_ip = args.target

        # Validate timeout
        valid_timeout, timeout_val = validate_timeout(args.timeout)
        if not valid_timeout:
            logger.error("Invalid timeout value")
            sys.exit(1)

        scanner(host_ip, args.start, args.end, timeout_val)

    main()