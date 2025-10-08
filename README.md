```
      _         
    / /\        
   / /  \       
  / / /\ \      
 / / /\ \ \     
/_/ /  \ \ \    
\ \ \   \ \ \   
 \ \ \   \ \ \  
  \ \ \___\ \ \ 
   \ \/____\ \ \
    \_________\/
```
# Zer0Specter

> A lightweight, multi-purpose cybersecurity toolkit for penetration testing, network analysis, and ethical hacking experiments.

Zer0Specter is a modular command-line framework built for learning and practical use in security research. It’s designed to be beginner-friendly while offering real-world utilities like password cracking, Wi-Fi deauthentication, IP geolocation, and more.


---

## 🔧 Features

- **ZIP Password Cracker**: Brute-force encrypted ZIP files using multiprocessing.
- **Secure Password Generator**: Create random, customizable passwords.
- **Wi-Fi Deauth Attack**: Perform deauthentication (DoS) attacks on Wi-Fi networks *(requires monitor mode)*.
- **IP Geolocation**: Retrieve geographic and ISP info for any IP address.
- **Packet Sniffer**: Real-time network traffic inspection with a clean, `tcpdump`-style output.
- **Port scanner**: A port scanner by brute force with banner detection.

---

## 📦 Requirements

You’ll need **Python 3.7+** and the following packages:

---

## Supported Platforms

- 🐧Linux - Fully support
- 🪟Windows - partial support — some features like Wi-Fi attacks may not work

---

## Found a bug? Have a suggestion?

Contributions, bug reports, and feature suggestions are welcome!
Please open an [Issue](https://github.com/Konazin/Zer0Specter/issues)  or contact me on GitHub.

```bash
pip install -r requirements.txt
```
## Author

- [Kona](https://github.com/Konazin)
