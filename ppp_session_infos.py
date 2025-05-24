import requests
from requests.auth import HTTPBasicAuth

base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

# Step 1: Get all subscribers
subs_url = f"{base_url}/rpc/get-subscribers/extensive"
subs_data = requests.get(subs_url, headers=headers, auth=auth).json()
subs = subs_data.get("subscribers-information", [])[0].get("subscriber", [])

# Step 2: For each subscriber with a pp0 interface, print subscriber + BNG session details
for s in subs:
    iface = s.get("interface", [{}])[0].get("data", "")
    if not iface.startswith("pp0."):
        continue

    print(f"\n🌐 PPP Session Interface: {iface}")
    
    # Subscriber info
    def safe(k): return s.get(k, [{}])[0].get("data", "N/A")

    print("📌 Subscriber Info:")
    print(f"  Username           : {safe('user-name')}")
    print(f"  Type               : {safe('access-type')}")
    print(f"  IP Address         : {safe('ip-address')}")
    print(f"  Routing Instance   : {safe('routing-instance')}")
    print(f"  MAC Address        : {safe('mac-address')}")
    print(f"  Session ID         : {safe('session-id')}")
    print(f"  State              : {safe('state')}")
    print(f"  Radius Accounting  : {safe('radius-accounting-id')}")
    print(f"  Login Time         : {safe('login-time')}")
    print(f"  NAS IP             : {safe('nas-ip-address')}")

    # Step 3: Pull BNG session details
    rpc_url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={iface}/extensive"
    data = requests.get(rpc_url, headers=headers, auth=auth).json()
    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])

    for sess in sessions:
        def g(key): return sess.get(key, [{}])[0].get("data", "N/A")

        print("📊 BNG Session Details:")
        print(f"  Phase              : {g('session-phase')}")
        print("  Keepalive:")
        ka = sess.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        print(f"    Interval         : {ka.get('keepalive-interval', [{}])[0].get('data', 'N/A')}")
        print(f"    Up Count         : {ka.get('keepalive-up-count', [{}])[0].get('data', 'N/A')}")
        print(f"    Down Count       : {ka.get('keepalive-down-count', [{}])[0].get('data', 'N/A')}")
        print(f"    Magic Validation : {ka.get('keepalive-magic-number-validation', [{}])[0].get('data', 'N/A')}")

        proto = sess.get("ppp-session-protocol-information", [{}])[0]
        print("  Protocol Info:")
        print(f"    Protocol         : {proto.get('ppp-protocol', [{}])[0].get('data', 'N/A')}")
        print(f"    State            : {proto.get('ppp-state', [{}])[0].get('data', 'N/A')}")
        print(f"    Last Start       : {proto.get('ppp-last-started', [{}])[0].get('data', 'N/A')}")
        print(f"    Last Completed   : {proto.get('ppp-last-completed', [{}])[0].get('data', 'N/A')}")
        print(f"    Negotiation Mode : {proto.get('ppp-negotiation-mode', [{}])[0].get('data', 'N/A')}")

        opts = proto.get("ppp-negotiated-options", [{}])[0]
        ipcp = opts.get("ipcp-address", [{}])[0]
        print("    IP Assignment:")
        print(f"      Local IP       : {ipcp.get('local-address', [{}])[0].get('data', 'N/A')}")
        print(f"      Remote IP      : {ipcp.get('remote-address', [{}])[0].get('data', 'N/A')}")
        print(f"      DNS Primary    : {opts.get('ipcp-primary-dns', [{}])[0].get('data', 'N/A')}")
        print(f"      DNS Secondary  : {opts.get('ipcp-secondary-dns', [{}])[0].get('data', 'N/A')}")

        auth = sess.get("ppp-auth-protocol-information", [{}])[0]
        print("  Auth Info:")
        print(f"    Protocol         : {auth.get('ppp-auth-proto', [{}])[0].get('data', 'N/A')}")
        print(f"    Result           : {auth.get('ppp-state', [{}])[0].get('data', 'N/A')}")
        print(f"    Last Start       : {auth.get('ppp-last-started', [{}])[0].get('data', 'N/A')}")
        print(f"    Last Completed   : {auth.get('ppp-last-completed', [{}])[0].get('data', 'N/A')}")

