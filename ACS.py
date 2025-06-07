import argparse
import subprocess
import json
from tabulate import tabulate
import urllib.parse

# Argument parser
parser = argparse.ArgumentParser(description='Query ACS and display device information')
parser.add_argument('--acs-ip', required=True, help='ACS server IP (e.g. 13.69.26.119)')
parser.add_argument('--client-id', required=True, help='Client _id (e.g. 40AE30-EX230v-22431)')
args = parser.parse_args()

# Encode the query like the original curl
query = urllib.parse.quote(json.dumps({"_id": args.client_id}))
url = f"http://{args.acs_ip}:7557/devices/?query={query}"

# Execute curl command
try:
    result = subprocess.run(["curl", "-s", "-i", url], capture_output=True, text=True, timeout=10)
    raw_output = result.stdout
except Exception as e:
    print(f"❌ Error executing curl: {e}")
    exit(1)

# Remove headers
try:
    body = raw_output.split("\r\n\r\n", 1)[1]
    json_data = json.loads(body)
    if not json_data:
        print("⚠️ No device found with this ID.")
        exit(0)
    device = json_data[0]
except Exception as e:
    print(f"❌ Failed to parse response: {e}")
    exit(1)

# Extract key values
info_table = [
    ["_id", device.get("_id", "N/A")],
    ["Last Inform", device.get("lastInform", "N/A")],
    ["Manufacturer", device.get("vendor", "N/A")],
    ["Model Name", device.get("modelName", "N/A")],
    ["Product Class", device.get("productClass", "N/A")],
    ["Serial Number", device.get("serialNumber", "N/A")],
    ["Software Version", device.get("softwareVersion", "N/A")],
    ["IP Address", device.get("ip", "N/A")],
    ["MAC Address", device.get("ethernetInterfaces", {}).get("0", {}).get("MACAddress", "N/A")],
]

# Display
print("\n📡 Device Information:\n")
print(tabulate(info_table, headers=["Field", "Value"], tablefmt="fancy_grid"))

