import argparse
import requests

def ip_locator(argus):
    parser = argparse.ArgumentParser(description="Geolocate an IP address")
    parser.add_argument("-ip", type=str, nargs='?', default=None, help="Target IP address (leave empty for your own IP)")
    args = parser.parse_args(argus)

    target_ip = args.ip if args.ip else ""
    try:
        url = f"https://ipwho.is/{target_ip}" if target_ip else "https://ipwho.is/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", True):
                print("----- Result -----")
                print(f"IP: {data.get('ip')}")
                print(f"Country: {data.get('country')}")
                print(f"Region: {data.get('region')}")
                print(f"City: {data.get('city')}")
                print(f"Connection Type: {data.get('type')}")
                print(f"Connection Type: {data.get('type')}")
                print(f"Latitude: {data.get('latitude')}")
                print(f"Longitude: {data.get('longitude')}")
                print("Connections: ")
                connection = data.get('connection')
                for name, value in connection.items():
                    print(f"{name} : {value}")
            else:
                print(f"[ERROR] API error: {data.get('message', 'Unknown')}")
        else:
            print(f"[ERROR] Request failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")