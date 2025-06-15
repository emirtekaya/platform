import argparse
import json
import urllib.parse
import requests
import sys
import time
import threading

ACS_BASE_URL = "http://13.69.26.119:7557/devices"

PARAMS = [
    "Device.PPP.Interface.2.IPCP.LocalIPAddress",
    "Device.PPP.Interface.2.Username",
    "Device.PPP.Interface.2.IPCP.RemoteIPAddress",
    "Device.PPP.Interface.2.IPCP.DNSServers",
    "Device.PPP.Interface.2.ConnectionStatus",
    "Device.PPP.Interface.2.CurrentMRUSize",
    "Device.PPP.Interface.2.AuthenticationProtocol",
    "Device.PPP.Interface.2.LCPEcho",
    "Device.PPP.Interface.2.LCPEchoRetry",
    "Device.PPP.Interface.2.LastConnectionError",
    "Device.PPP.Interface.2.PPPoE.ACName",
    "Device.PPP.Interface.2.PPPoE.ServiceName",
    "Device.PPP.Interface.2.PPPoE.SessionID",
    "Device.PPP.SupportedNCPs"
]

FIELD_MAP = {
    "mac": "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.MACAddress",
    "ip": "Device.PPP.Interface.2.IPCP.LocalIPAddress",
    "ppp": "VirtualParameters.PPPoEUsername"
}

def spinner(message, event):
    spinstr = "|/-\\"
    idx = 0
    while not event.is_set():
        sys.stdout.write(f"\r{message} {spinstr[idx % len(spinstr)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.2)
    sys.stdout.write("\r")

def main():
    parser = argparse.ArgumentParser(description="Search and refresh device info from ACS")
    parser.add_argument("search_type", choices=["mac", "ip", "ppp"], help="Type of search")
    parser.add_argument("search_value", help="Value to search for")
    args = parser.parse_args()

    field = FIELD_MAP[args.search_type]
    query = urllib.parse.quote(json.dumps({field: args.search_value}))
    url = f"{ACS_BASE_URL}/?query={query}"

    event = threading.Event()
    thread = threading.Thread(target=spinner, args=("🔍 Searching device ID", event))
    thread.start()

    try:
        response = requests.get(url)
        event.set()
        thread.join()
        device_list = response.json()
        device_id = device_list[0]["_id"] if device_list else None
    except Exception as e:
        event.set()
        thread.join()
        print(f"\n❌ Error retrieving device ID: {e}")
        sys.exit(1)

    if not device_id:
        print(f"❌ Device not found for {args.search_type}: {args.search_value}")
        sys.exit(1)

    print(f"✅ Found device ID: {device_id}")

    encoded_id = urllib.parse.quote(device_id)
    post_url = f"{ACS_BASE_URL}/{encoded_id}/tasks?connection_request"
    payload = {"name": "refreshObject", "objectName": ""}

    event.clear()
    thread = threading.Thread(target=spinner, args=("⚙️  Sending refreshObject task", event))
    thread.start()

    try:
        response = requests.post(post_url, json=payload)
        event.set()
        thread.join()
        if response.status_code == 200:
            print("✅ refreshObject task sent successfully.")
        else:
            print(f"❌ Failed to send refreshObject task. HTTP {response.status_code}")
            print(response.text)
            sys.exit(1)
    except Exception as e:
        event.set()
        thread.join()
        print(f"\n❌ Error sending refreshObject task: {e}")
        sys.exit(1)

    projection = urllib.parse.quote(",".join(PARAMS))
    query_id = urllib.parse.quote(json.dumps({"_id": device_id}))
    full_url = f"{ACS_BASE_URL}?query={query_id}&projection={projection}"

    try:
        response = requests.get(full_url)
        data = response.json()
        print("📥 Retrieved parameter values:")
        for param in PARAMS:
            path = param.split(".")
            val = data[0]
            for p in path:
                val = val.get(p, {})
            print(f"➡️  {param} = {val.get('_value', '❌ no value')}")
    except Exception as e:
        print(f"❌ Error retrieving parameters: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

