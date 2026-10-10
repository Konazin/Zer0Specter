"""Retrieve geolocation information for an IP address."""

import argparse
from typing import List

import requests

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import validate_ip_address


def ip_locator(argus: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Geolocate an IP address")
    parser.add_argument(
        "-ip",
        dest="ip",
        nargs="?",
        default=None,
        help="target IP address (leave empty to locate this connection)",
    )
    args = parser.parse_args(argus)
    logger = get_logger()

    if args.ip and not validate_ip_address(args.ip):
        parser.error("target must be a valid IPv4 or IPv6 address")

    url = f"https://ipwho.is/{args.ip}" if args.ip else "https://ipwho.is/"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as error:
        logger.error("Geolocation request failed (%s)", type(error).__name__)
        return 1

    if response.status_code != 200:
        logger.error("Geolocation service returned HTTP %s", response.status_code)
        return 1

    try:
        data = response.json()
    except ValueError:
        logger.error("Geolocation service returned invalid JSON")
        return 1

    if (
        not isinstance(data, dict)
        or data.get("success") is not True
        or not data.get("ip")
    ):
        logger.error("Geolocation service could not resolve the requested address")
        return 1

    print("----- Result -----")
    for label, field in (
        ("IP", "ip"),
        ("Country", "country"),
        ("Region", "region"),
        ("City", "city"),
        ("Connection Type", "type"),
        ("Latitude", "latitude"),
        ("Longitude", "longitude"),
    ):
        print(f"{label}: {data.get(field)}")

    connection = data.get("connection")
    if isinstance(connection, dict) and connection:
        print("Connection:")
        for name, value in connection.items():
            print(f"{name}: {value}")
    return 0
