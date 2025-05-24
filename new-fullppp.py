import requests
from requests.auth import HTTPBasicAuth
from tabulate import tabulate

# === Configuration ===
base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

def safe_get(obj, *keys):
    """Safely extract nested values"""
    for key in keys:
        obj = obj.get(key, [{}])[0]
    return obj.get("data", "N/A")

print("🔍 Fetching subscribers from ACS...")
try:
    subs_url = f"{base_url}/rpc/get-subscribers/extensive"
    response = requests.get(subs_url, headers=headers, auth=auth, timeout=60)
    subs_data = response.json()
except Exception as e:
    print(f"❌ Error fetching subscribers: {e}")
    exit(1)

# === Extract PPPoE sessions ===
print("📡 Extracting active PPPoE sessions...")
ppps = []
subscribers = subs_data.get("subscribers-information", [])[0].get("subscriber", [])
for s in subscribers:
    iface = safe_get(s, "interface")
    access_type = safe_get(s, "access-type")
    if iface.startswith("pp0.") and access_type == "PPPoE":
        ppps.append((iface, s))

print(f"✅ Found {len(ppps)} PPPoE session(s).\n")

# === Process Each PPPoE Session ===
for pp_if, subscriber in ppps:
    print("\n" + "=" * 90)
    print(f"📶 PPP Session: {pp_if}")
    print("=" * 90)

    sub_info = [
        ["Username", safe_get(subscriber, "user-name")],
        ["Type", safe_get(subscriber, "access-type")],
        ["IP Address", safe_get(subscriber, "ip-address")],
        ["Routing Instance", safe_get(subscriber, "routing-instance")],
        ["MAC Address", safe_get(subscriber, "mac-address")],
        ["Session ID", safe_get(subscriber, "session-id")],
        ["State", safe_get(subscriber, "state")],
        ["Radius Accounting", safe_get(subscriber, "radius-accounting-id")],
        ["Login Time", safe_get(subscriber, "login-time")],
        ["NAS IP", safe_get(subscriber, "nas-ip-address")],
    ]
    print(tabulate(sub_info, headers=["Subscriber Info", "Value"], tablefmt="fancy_grid"))

    # --- Fetch Detailed PPP Info ---
    print(f"📨 Querying detailed PPP info for {pp_if}...")
    try:
        url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp_if}/extensive"
        ppp_resp = requests.get(url, headers=headers, auth=auth, timeout=30).json()
    except Exception as e:
        print(f"❌ Failed to get details for {pp_if}: {e}")
        continue

    sessions = ppp_resp.get("ppp-interface-information", [])[0].get("ppp-session", [])
    for s in sessions:
        # Keepalive
        ka = s.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        keepalive = [
            ["Interval", safe_get(ka, "keepalive-interval")],
            ["Up Count", safe_get(ka, "keepalive-up-count")],
            ["Down Count", safe_get(ka, "keepalive-down-count")],
            ["Magic Validation", safe_get(ka, "keepalive-magic-number-validation")],
        ]

        # Protocol Info
        protocol_info, ip_info = [], []
        for section in s.get("ppp-session-protocol-information", []):
            protocol_info += [
                ["Protocol", safe_get(section, "ppp-protocol")],
                ["State", safe_get(section, "ppp-state")],
                ["Last Start", safe_get(section, "ppp-last-started")],
                ["Last Completed", safe_get(section, "ppp-last-completed")],
                ["Negotiation Mode", safe_get(section, "ppp-negotiation-mode")],
            ]

            opts = section.get("ppp-negotiated-options", [{}])[0]
            ipcp = opts.get("ipcp-address", [{}])[0]
            ip_info = [
                ["Local IP", safe_get(ipcp, "local-address")],
                ["Remote IP", safe_get(ipcp, "remote-address")],
                ["DNS Primary", safe_get(opts, "ipcp-primary-dns")],
                ["DNS Secondary", safe_get(opts, "ipcp-secondary-dns")],
            ]

        # Auth Info
        auth_info = []
        for section in s.get("ppp-auth-protocol-information", []):
            auth_info = [
                ["Protocol", safe_get(section, "ppp-auth-proto")],
                ["Result", safe_get(section, "ppp-state")],
                ["Last Start", safe_get(section, "ppp-last-started")],
                ["Last Completed", safe_get(section, "ppp-last-completed")],
            ]

        # Display Tables
        print(tabulate(keepalive, headers=["Keepalive", "Value"], tablefmt="fancy_grid"))
        print(tabulate(protocol_info, headers=["Protocol Info", "Value"], tablefmt="fancy_grid"))
        print(tabulate(ip_info, headers=["IP Assignment", "Value"], tablefmt="fancy_grid"))
        print(tabulate(auth_info, headers=["Auth Info", "Value"], tablefmt="fancy_grid"))

