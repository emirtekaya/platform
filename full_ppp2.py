import argparse
import requests
from requests.auth import HTTPBasicAuth
from tabulate import tabulate
import sys

# Set up command-line arguments
parser = argparse.ArgumentParser(description='PPP Session Analyzer')
parser.add_argument('-m', '--mac', help='Filter by MAC address (case-insensitive)')
parser.add_argument('-id', '--session-id', help='Filter by Session ID')
args = parser.parse_args()

base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

try:
    # Get all subscribers
    subs_url = f"{base_url}/rpc/get-subscribers/extensive"
    response = requests.get(subs_url, headers=headers, auth=auth, timeout=60)
    response.raise_for_status()
    subs = response.json()
except requests.exceptions.RequestException as e:
    print(f"🚨 API Error: {str(e)}")
    sys.exit(1)

# Validate API response structure
try:
    subscribers = subs["subscribers-information"][0]["subscriber"]
except (KeyError, IndexError, TypeError):
    print("❌ Unexpected API response structure")
    sys.exit(1)

# Extract and filter PPPoE sessions
ppps = []
found_session_id = False  # Track if we've seen the requested session ID

for s in subscribers:
    try:
        # Check for session ID match first
        current_id = s.get("session-id", [{}])[0].get("data", "")
        if args.session_id and current_id == args.session_id:
            found_session_id = True
            
        # Interface check
        iface_data = s.get("interface", [{}])
        iface = iface_data[0].get("data", "") if iface_data else ""
        
        # Access type check
        access_data = s.get("access-type", [{}])
        access_type = access_data[0].get("data", "") if access_data else ""
        
        # Skip non-PPPoE sessions
        if not (iface.startswith("pp0.") and access_type == "PPPoE"):
            continue
            
        # Get identifiers
        session_mac = s.get("mac-address", [{}])[0].get("data", "").lower()
        session_id = current_id

        # Apply filters
        mac_match = not args.mac or (args.mac and args.mac.lower() == session_mac)
        id_match = not args.session_id or (args.session_id == session_id)
        
        if mac_match and id_match:
            ppps.append((iface, s))
            
    except Exception as e:
        print(f"⚠️ Error processing entry: {str(e)}")
        continue

# Special case handling for session ID
if args.session_id and not ppps and found_session_id:
    print(f"ℹ️ Session ID '{args.session_id}' exists but is not an active PPPoE session")
    sys.exit(0)

if not ppps:
    print("❌ No matching PPPoE sessions found")
    if args.session_id:
        print(f"Checked Session ID: {args.session_id}")
    if args.mac:
        print(f"Checked MAC Address: {args.mac}")
    sys.exit(0)

# Rest of your original processing code...

# Process matching sessions
for pp_if, subscriber in ppps:
    print("\n" + "=" * 90)
    print(f"📡 PPP Session Interface: {pp_if}")
    print("=" * 90)

    # Subscriber Info Table
    sub_info = [
        ["Username", subscriber.get("user-name", [{}])[0].get("data", "N/A")],
        ["Type", subscriber.get("access-type", [{}])[0].get("data", "N/A")],
        ["IP Address", subscriber.get("ip-address", [{}])[0].get("data", "N/A")],
        ["Routing Instance", subscriber.get("routing-instance", [{}])[0].get("data", "N/A")],
        ["MAC Address", subscriber.get("mac-address", [{}])[0].get("data", "N/A")],
        ["Session ID", subscriber.get("session-id", [{}])[0].get("data", "N/A")],
        ["State", subscriber.get("state", [{}])[0].get("data", "N/A")],
        ["Radius Accounting", subscriber.get("radius-accounting-id", [{}])[0].get("data", "N/A")],
        ["Login Time", subscriber.get("login-time", [{}])[0].get("data", "N/A")],
        ["NAS IP", subscriber.get("nas-ip-address", [{}])[0].get("data", "N/A")],
    ]
    print(tabulate(sub_info, headers=["Subscriber Info", "Value"], tablefmt="fancy_grid"))

    # Get detailed PPP info
    url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp_if}/extensive"
    resp = requests.get(url, headers=headers, auth=auth)
    data = resp.json()
    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])

    for s in sessions:
        def safe(key): return s.get(key, [{}])[0].get("data", "N/A")

        # Keepalive information
        ka = s.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        keepalive = [
            ["Interval", ka.get("keepalive-interval", [{}])[0].get("data", "N/A")],
            ["Up Count", ka.get("keepalive-up-count", [{}])[0].get("data", "N/A")],
            ["Down Count", ka.get("keepalive-down-count", [{}])[0].get("data", "N/A")],
            ["Magic Validation", ka.get("keepalive-magic-number-validation", [{}])[0].get("data", "N/A")],
        ]

        # Protocol information
        protocol_info = []
        ip_info = []
        for section in s.get("ppp-session-protocol-information", []):
            proto = section.get("ppp-protocol", [{}])[0].get("data", "N/A")
            state = section.get("ppp-state", [{}])[0].get("data", "N/A")
            start = section.get("ppp-last-started", [{}])[0].get("data", "N/A")
            done = section.get("ppp-last-completed", [{}])[0].get("data", "N/A")
            mode = section.get("ppp-negotiation-mode", [{}])[0].get("data", "N/A")
            
            protocol_info.extend([
                ["Protocol", proto],
                ["State", state],
                ["Last Start", start],
                ["Last Completed", done],
                ["Negotiation Mode", mode]
            ])

            # IP information
            opts = section.get("ppp-negotiated-options", [{}])[0]
            ipcp = opts.get("ipcp-address", [{}])[0]
            local_ip = ipcp.get("local-address", [{}])[0].get("data", "N/A")
            remote_ip = ipcp.get("remote-address", [{}])[0].get("data", "N/A")
            dns1 = opts.get("ipcp-primary-dns", [{}])[0].get("data", "N/A")
            dns2 = opts.get("ipcp-secondary-dns", [{}])[0].get("data", "N/A")

            ip_info = [
                ["Local IP", local_ip],
                ["Remote IP", remote_ip],
                ["DNS Primary", dns1],
                ["DNS Secondary", dns2],
            ]

        # Authentication information
        auth_info = []
        for section in s.get("ppp-auth-protocol-information", []):
            proto = section.get("ppp-auth-proto", [{}])[0].get("data", "N/A")
            result = section.get("ppp-state", [{}])[0].get("data", "N/A")
            start = section.get("ppp-last-started", [{}])[0].get("data", "N/A")
            done = section.get("ppp-last-completed", [{}])[0].get("data", "N/A")
            
            auth_info = [
                ["Protocol", proto],
                ["Result", result],
                ["Last Start", start],
                ["Last Completed", done],
            ]

        # Print all tables
        print(tabulate(keepalive, headers=["Keepalive", "Value"], tablefmt="fancy_grid"))
        print(tabulate(protocol_info, headers=["Protocol Info", "Value"], tablefmt="fancy_grid"))
        print(tabulate(ip_info, headers=["IP Assignment", "Value"], tablefmt="fancy_grid"))
        print(tabulate(auth_info, headers=["Auth Info", "Value"], tablefmt="fancy_grid"))
