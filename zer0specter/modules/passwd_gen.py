import argparse
import string
import random

def password_generator(arguments):
    parser = argparse.ArgumentParser(description="Generate a random secure password")
    parser.add_argument("-px", "--prefix", dest="prefix", type=str, help="password prefix if you want")
    parser.add_argument("-nc", "--numberchar", dest="length", type=int, required=True, help="Password length")
    parser.add_argument("-p", "--punctuation", dest="use_punct", help="Include special characters? (y/n)", default="n")
    parser.add_argument("-n", "--numbers", dest="use_nums", help="Include numbers? (y/n)", default="n")
    parser.add_argument("-up", "--uppercase", dest="use_upper", help="Include uppercase letters? (y/n)", default="n")
    args = parser.parse_args(arguments)

    charset = string.ascii_lowercase
    if (args.use_punct).lower() == 'y':
        charset += string.punctuation
    if (args.use_nums).lower() == 'y':
        charset += string.digits
    if (args.use_upper).lower() == 'y':
        charset += string.ascii_uppercase

    password = ''.join(random.choice(charset) for _ in range(args.length))
    if args.prefix:
        print(args.prefix + password)
    else:
        print(password)