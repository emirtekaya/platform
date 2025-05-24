import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

# === BNG CONNECTION CONFIG ===
BASE_URL = "http://213.133.212.24:2000"
AUTH = HTTPBasicAuth("support", "sabel2025!")
HEADERS = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}

# === STEP 1: CALL get-subscribers/extensive ===
url = f"{BASE_URL}/rpc/get-subscribers/extensive"
response = requests.get(url, headers=HEADERS, auth=AUTH)
data = response.json()

# === STEP 2: PARSE subscriber info ===
subs = data.get("subscribers-information", [])[0].get("subscriber", [])

def extract(key, entry):
    return entry.get(key, [{}])[0].get("data", "N/A")

parsed = []
for sub in subs:
    interface = extract("interface", sub)
    if not interface.startswith("pp0"):
        continue

    parsed.append({
        "PPP Session": interface,
        "Username": extract("user-name", sub),
        "IP Address": extract("ip-address", sub),
        "MAC Address": extract("mac-address", sub),
        "NAS IP": extract("nas-ip-address", sub),
        "State": extract("state", sub),
        "Session ID": extract("session-id", sub),
        "Routing Instance": extract("routing-instance", sub),
        "Login Time": extract("login-time", sub),
        "Radius Acct ID": extract("radius-accounting-id", sub)
    })

# === STEP 3: DISPLAY OR EXPORT ===
df = pd.DataFrame(parsed)

# Print table to terminal
print(df.to_string(index=False))

# Optional: export to Excel
# df.to_excel("pppoe_subscribers.xlsx", index=False)

