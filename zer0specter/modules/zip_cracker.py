"""Search ZIP passwords with a wordlist or a bounded character set."""

import argparse
import os
import string
from itertools import product
from multiprocessing import Pool, cpu_count
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterable, Optional, Tuple

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import (
    validate_directory_path,
    validate_file_path,
    validate_input_range,
)


def worker_try_password(args_tuple: Tuple[str, str]) -> Tuple[str, bool]:
    """Check a candidate by reading archive data without extracting it."""
    password, zip_path = args_tuple
    try:
        import pyzipper

        with pyzipper.AESZipFile(zip_path, "r") as archive:
            encrypted_files = [
                member
                for member in archive.infolist()
                if not member.is_dir() and member.flag_bits & 0x1
            ]
            if not encrypted_files:
                return password, False

            for member in encrypted_files:
                with archive.open(member, "r", pwd=password.encode()) as source:
                    while source.read(64 * 1024):
                        pass
        return password, True
    except Exception:
        return password, False


def _safe_to_extract(archive, destination: Path) -> bool:
    """Reject member names that escape the selected output directory."""
    root = destination.resolve()
    seen = set()
    for member in archive.infolist():
        name = member.filename.replace("\\", "/")
        path = PurePosixPath(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or any(":" in part for part in path.parts)
        ):
            return False
        target = (root / Path(*path.parts)).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            return False
        if target in seen or target.exists():
            return False
        seen.add(target)
    return True


def _password_candidates(
    wordlist: Optional[str], charset: str, length: Optional[int], zip_path: str
) -> Iterable[Tuple[str, str]]:
    if wordlist:
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as source:
            for line in source:
                password = line.strip()
                if password:
                    yield password, zip_path
        return

    for combination in product(charset, repeat=length):
        yield "".join(combination), zip_path


def zipcrack(argus: list) -> int:
    """Search for a ZIP password and extract once after a match."""
    parser = argparse.ArgumentParser(description="Crack password-protected ZIP files")
    parser.add_argument("-w", "--wordlist", default=None, help="wordlist file")
    parser.add_argument("-l", "--letters", choices=("y", "n", "Y", "N"), default="n")
    parser.add_argument("-n", "--numbers", choices=("y", "n", "Y", "N"), default="n")
    parser.add_argument(
        "-sc", "--specialcharacters", choices=("y", "n", "Y", "N"), default="n"
    )
    parser.add_argument(
        "-s", "--size", type=int, help="candidate length for brute force"
    )
    parser.add_argument("-p", "--path", required=True, help="target ZIP file")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="extraction directory (default: current directory)",
    )
    args = parser.parse_args(argus)
    logger = get_logger()

    valid_zip, zip_error = validate_file_path(args.path)
    if not valid_zip:
        logger.error("Invalid ZIP file: %s", zip_error)
        return 2

    if args.wordlist:
        valid_wordlist, wordlist_error = validate_file_path(args.wordlist)
        if not valid_wordlist:
            logger.error("Invalid wordlist file: %s", wordlist_error)
            return 2

    if args.output_dir:
        output_dir = Path(args.output_dir)
        valid_output, _ = validate_directory_path(output_dir)
        if not valid_output or not os.access(output_dir, os.W_OK):
            logger.error("Output directory must exist and be writable")
            return 2
    else:
        output_dir = Path.cwd()

    if args.size is not None:
        valid_length, length = validate_input_range(args.size, 1, 10)
        if not valid_length:
            parser.error("size must be between 1 and 10")
    else:
        length = None

    charset = ""
    if args.letters.lower() == "y":
        charset += string.ascii_letters
    if args.numbers.lower() == "y":
        charset += string.digits
    if args.specialcharacters.lower() == "y":
        charset += string.punctuation

    if not args.wordlist and not charset:
        parser.error("provide a wordlist or select at least one character set")
    if not args.wordlist and length is None:
        parser.error("--size is required for brute-force mode")

    candidates = _password_candidates(args.wordlist, charset, length, args.path)
    found_password: Optional[str] = None
    logger.info("Starting ZIP password search")

    try:
        with Pool(cpu_count()) as pool:
            for password, success in pool.imap_unordered(
                worker_try_password, candidates, chunksize=500
            ):
                if success:
                    found_password = password
                    pool.terminate()
                    break
    except KeyboardInterrupt:
        logger.warning("ZIP password search interrupted")
        return 130
    except Exception as error:
        logger.error("ZIP password search failed (%s)", type(error).__name__)
        return 1

    if found_password is None:
        logger.info("Password was not found in the supplied search space")
        return 0

    try:
        import pyzipper

        with pyzipper.AESZipFile(args.path, "r") as archive:
            if not _safe_to_extract(archive, output_dir):
                logger.error("Archive contains unsafe or conflicting output paths")
                return 1
            archive.extractall(path=output_dir, pwd=found_password.encode())
    except Exception as error:
        logger.error("ZIP extraction failed (%s)", type(error).__name__)
        return 1

    print(found_password)
    logger.info("ZIP password found and archive extracted")
    return 0
