"""Generate random passwords for the command line."""

import argparse
import secrets
import string
from typing import List

from zer0specter.utils.validators import validate_password_length


def password_generator(arguments: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a secure password")
    parser.add_argument(
        "-px", "--prefix", dest="prefix", help="optional password prefix"
    )
    parser.add_argument(
        "-nc",
        "--numberchar",
        dest="length",
        type=int,
        required=True,
        help="number of generated characters",
    )
    parser.add_argument(
        "-p",
        "--punctuation",
        dest="use_punct",
        choices=("y", "Y", "n", "N"),
        default="n",
        help="include special characters",
    )
    parser.add_argument(
        "-n",
        "--numbers",
        dest="use_nums",
        choices=("y", "Y", "n", "N"),
        default="n",
        help="include numbers",
    )
    parser.add_argument(
        "-up",
        "--uppercase",
        dest="use_upper",
        choices=("y", "Y", "n", "N"),
        default="n",
        help="include uppercase letters",
    )
    args = parser.parse_args(arguments)

    valid_length, length = validate_password_length(args.length)
    if not valid_length:
        parser.error("password length must be between 1 and 1000")

    charset = string.ascii_lowercase
    if args.use_punct.lower() == "y":
        charset += string.punctuation
    if args.use_nums.lower() == "y":
        charset += string.digits
    if args.use_upper.lower() == "y":
        charset += string.ascii_uppercase

    password = "".join(secrets.choice(charset) for _ in range(length))
    print(f"{args.prefix or ''}{password}")
    return 0
