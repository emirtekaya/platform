import requests
import json
from requests.auth import HTTPBasicAuth

# Base config
base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

# STEP 1: Get all active subscribers
print("🔄 Fetching active subscribers...")
subs_url = f"{base_url}/rpc/get-subscribers/extensive"
subs_resp = requests.get(subs_url, headers=headers, auth=auth, timeout=60)
subs_data = subs_resp.json()

# STEP 2: Extract all pp0.xxx interfaces
ppp_ids = []
for subscriber in subs_data.get("subscribers-information", [])[0].get("subscriber", []):
    iface = subscriber.get("interface", [{}])[0].get("data", "")
    if iface.startswith("pp0."):
        ppp_ids.append(iface)

print(f"\n✅ Found {len(ppp_ids)} PPP sessions.")

# STEP 3: Fetch and dump each PPP session info
for pp_iface in ppp_ids:
    print(f"\n🔍 Requesting session: {pp_iface}")
    rpc_url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp_iface}/extensive"
    resp = requests.get(rpc_url, headers=headers, auth=auth)
    data = resp.json()

    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])
    if not sessions:
        print("❌ No session data returned.")
        continue

    for session in sessions:
        print(f"\n🧾 Full raw JSON for {pp_iface}:\n")
        print(json.dumps(session, indent=2))  # dump the whole thing

        print("\n🧪 Session fields present:")
        for key in session:
            print(f"  - {key}")

