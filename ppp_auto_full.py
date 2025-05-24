import requests
from requests.auth import HTTPBasicAuth

base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

# STEP 1: Get subscribers
subs_url = f"{base_url}/rpc/get-subscribers/extensive"
subs = requests.get(subs_url, headers=headers, auth=auth, timeout=60).json()
import json

# DEBUG: Show full subscriber info to understand structure
for s in subs.get("subscribers-information", [])[0].get("subscriber", []):
    print("🔎 Full subscriber entry:")
    print(json.dumps(s, indent=2))

# STEP 2: Extract all pp0.xxxx session interfaces
ppps = []
for s in subs.get("subscribers-information", [])[0].get("subscriber", []):
    iface = s.get("interface", [{}])[0].get("data", "")
    if iface.startswith("pp0."):
        ppps.append(iface)

# STEP 3: Parse each session in depth
for pp in ppps:
    print(f"\n─────────────────────────────────────────────")
    print(f"        🔍 Detailed Info for {pp}        ")
    print(f"─────────────────────────────────────────────")
    
    url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp}/extensive"
    resp = requests.get(url, headers=headers, auth=auth)
    data = resp.json()
    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])
    for s in sessions:
        def safe(key): return s.get(key, [{}])[0].get("data", "N/A")

        print(f"Session Name          : {safe('session-name')}")
        print(f"Session Type          : {safe('session-type')}")
        print(f"Session Phase         : {safe('session-phase')}")
        print(f"Session State         : {safe('session-state')}")
        print(f"Uptime                : {safe('session-uptime')}")
        print(f"Termination Reason    : {safe('session-termination-reason')}")
        print(f"Underlying Interface  : {safe('underlying-interface')}")
        print(f"Framing Type          : {safe('framing-type')}")
        print(f"Authentication Protocol : {safe('authentication-protocol')}")
        print(f"Authentication Result : {safe('authentication-result')}")
        print(f"Framing Error         : {safe('framing-error')}")
        print(f"Session Flags         : {safe('session-flags')}")
        
        # Keepalive
        ka = s.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        print("Keepalive:")
        print(f"  Interval            : {ka.get('keepalive-interval', [{}])[0].get('data', 'N/A')}")
        print(f"  Up Count            : {ka.get('keepalive-up-count', [{}])[0].get('data', 'N/A')}")
        print(f"  Down Count          : {ka.get('keepalive-down-count', [{}])[0].get('data', 'N/A')}")
        print(f"  Magic Validation    : {ka.get('keepalive-magic-number-validation', [{}])[0].get('data', 'N/A')}")

        # Protocols: LCP/NCP/CHAP/PAP/etc
        protocols = s.get("ppp-session-protocol-information", [{}])[0]
        if protocols:
            print("Protocol States:")
            for proto_name, proto_val in protocols.items():
                if isinstance(proto_val, list) and proto_val and 'data' in proto_val[0]:
                    print(f"  {proto_name:<22}: {proto_val[0]['data']}")

