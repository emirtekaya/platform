import requests
from requests.auth import HTTPBasicAuth

base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

# STEP 1: Get current subscribers
subs_url = f"{base_url}/rpc/get-subscribers/extensive"
subs_data = requests.get(subs_url, headers=headers, auth=auth).json()

ppps = []
for s in subs_data.get("subscribers-information", [])[0].get("subscriber", []):
    iface = s.get("interface", [{}])[0].get("data", "")
    if iface.startswith("pp0."):
        ppps.append(iface)

for pp in ppps:
    print(f"\n🛰️  PPP Session: {pp}")
    url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp}/extensive"
    data = requests.get(url, headers=headers, auth=auth).json()

    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])
    for s in sessions:
        def g(key): return s.get(key, [{}])[0].get("data", "N/A")

        print(f"  Type                : {g('session-type')}")
        print(f"  Phase               : {g('session-phase')}")
        print("  Keepalive:")
        ka = s.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        print(f"    Interval          : {ka.get('keepalive-interval', [{}])[0].get('data', 'N/A')}")
        print(f"    Up Count          : {ka.get('keepalive-up-count', [{}])[0].get('data', 'N/A')}")
        print(f"    Down Count        : {ka.get('keepalive-down-count', [{}])[0].get('data', 'N/A')}")
        print(f"    Magic Validation  : {ka.get('keepalive-magic-number-validation', [{}])[0].get('data', 'N/A')}")

        # Protocol info
        proto = s.get("ppp-session-protocol-information", [{}])[0]
        print("  Protocol Info:")
        print(f"    Protocol          : {proto.get('ppp-protocol', [{}])[0].get('data', 'N/A')}")
        print(f"    State             : {proto.get('ppp-state', [{}])[0].get('data', 'N/A')}")
        print(f"    Negotiation Mode  : {proto.get('ppp-negotiation-mode', [{}])[0].get('data', 'N/A')}")

        # IPCP/PPP IP info
        if "ppp-negotiated-options" in proto:
            opts = proto["ppp-negotiated-options"][0]
            ipcp = opts.get("ipcp-address", [{}])[0]
            print("    IP Assignment:")
            print(f"      Local IP        : {ipcp.get('local-address', [{}])[0].get('data', 'N/A')}")
            print(f"      Remote IP       : {ipcp.get('remote-address', [{}])[0].get('data', 'N/A')}")
            print(f"      DNS Primary     : {opts.get('ipcp-primary-dns', [{}])[0].get('data', 'N/A')}")
            print(f"      DNS Secondary   : {opts.get('ipcp-secondary-dns', [{}])[0].get('data', 'N/A')}")

        # Auth info
        auth_info = s.get("ppp-auth-protocol-information", [{}])[0]
        print("  Auth Info:")
        print(f"    Protocol          : {auth_info.get('ppp-auth-proto', [{}])[0].get('data', 'N/A')}")
        print(f"    Result            : {auth_info.get('ppp-state', [{}])[0].get('data', 'N/A')}")

