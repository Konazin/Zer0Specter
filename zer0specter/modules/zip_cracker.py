import argparse
import string
from itertools import product
import pyzipper
from multiprocessing import Pool, cpu_count
import os
from typing import Optional, Tuple

from zer0specter.utils.logger import get_logger
from zer0specter.utils.validators import validate_file_path, validate_input_range

logger = get_logger()

def worker_try_password(args_tuple: Tuple[str, str]) -> Tuple[str, bool]:
    """Worker function to test a single password."""
    password, zip_path = args_tuple
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zf:
            zf.extractall(pwd=password.encode())
        return (password, True)
    except Exception:
        return (password, False)

def zipcrack(argus: list) -> None:
    """ZIP file password cracker using brute force or wordlist attack."""

    parser = argparse.ArgumentParser(description="Crack password-protected ZIP files")
    parser.add_argument("-w", "--wordlist", dest="wordlist", help="Path to wordlist file", default=None)
    parser.add_argument("-l", "--letters", dest="use_letters", help="Include letters (y/n)", default='n')
    parser.add_argument("-n", "--numbers", dest="use_numbers", help="Include digits (y/n)", default='n')
    parser.add_argument("-sc", "--specialcharacters", dest="use_special", help="Include special characters (y/n)", default='n')
    parser.add_argument("-s", "--size", dest="length", type=int, help="Password length to test (for brute force)")
    parser.add_argument("-p", "--path", dest="zip_path", required=True, help="Path to the target ZIP file")
    args = parser.parse_args(argus)

    # Validate ZIP file path
    valid_file, error_msg = validate_file_path(args.zip_path)
    if not valid_file:
        logger.error(f"Invalid ZIP file: {error_msg}")
        return

    # Validate password length if provided
    if args.length is not None:
        valid_length, length_val = validate_input_range(args.length, 1, 10)  # Reasonable limit
        if not valid_length:
            logger.error("Invalid password length (must be 1-10)")
            return
        args.length = length_val

    # Build character set
    charset = ""
    if args.use_letters.lower() == 'y':
        charset += string.ascii_letters
    if args.use_numbers.lower() == 'y':
        charset += string.digits
    if args.use_special.lower() == 'y':
        charset += string.punctuation

    # If no charset and no wordlist, error
    if not charset and not args.wordlist:
        logger.error("No character set selected and no wordlist provided")
        return

    # If wordlist provided, validate it
    if args.wordlist:
        valid_wordlist, wordlist_error = validate_file_path(args.wordlist)
        if not valid_wordlist:
            logger.error(f"Invalid wordlist file: {wordlist_error}")
            return

    def generate_combinations():
        """Generate password combinations."""
        if args.wordlist:
            # Wordlist mode
            try:
                with open(args.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        password = line.strip()
                        if password:  # Skip empty lines
                            yield (password, args.zip_path)
            except Exception as e:
                logger.error(f"Error reading wordlist: {e}")
                return
        else:
            # Brute force mode
            for combo in product(charset, repeat=args.length):
                yield (''.join(combo), args.zip_path)

    logger.info(f"Starting password cracking on {args.zip_path}")
    if args.wordlist:
        logger.info(f"Using wordlist: {args.wordlist}")
    else:
        logger.info(f"Brute force with charset: '{charset}' and length: {args.length}")

    found_password: Optional[str] = None

    try:
        with Pool(cpu_count()) as pool:
            total = 0
            for password, success in pool.imap_unordered(worker_try_password, generate_combinations(), chunksize=500):
                total += 1
                if total % 1000 == 0:  # Log progress every 1000 attempts
                    logger.info(f"Tested {total} passwords...")

                if success:
                    found_password = password
                    logger.info(f"PASSWORD FOUND: {password}")
                    pool.terminate()
                    break

        if found_password:
            logger.info(f"Successfully cracked ZIP file with password: {found_password}")
        else:
            logger.warning("Password not found in the search space")

    except KeyboardInterrupt:
        logger.info("Password cracking interrupted by user")
    except Exception as e:
        logger.error(f"Error during password cracking: {e}")