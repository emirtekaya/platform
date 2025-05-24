import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

# === CONFIGURATION ===
BASE_URL = "http://213.133.212.24:2000"
AUTH = HTTPBasicAuth("support", "sabel2025!")
HEADERS = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}
URL = f"{BASE_URL}/rpc/get-interface-information/terse"

# === MAKE THE RPC CALL ===
response = requests.get(URL, headers=HEADERS, auth=AUTH)
data = response.json()

# === PARSE AND ORGANIZE THE RESULT ===
organized = []

for phy in data.get("interface-information", [])[0].get("physical-interface", []):
    p_name = phy.get("name", [{}])[0].get("data", "N/A")
    p_admin = phy.get("admin-status", [{}])[0].get("data", "N/A")
    p_oper = phy.get("oper-status", [{}])[0].get("data", "N/A")

    for logi in phy.get("logical-interface", []):
        l_name = logi.get("name", [{}])[0].get("data", "N/A")
        l_admin = logi.get("admin-status", [{}])[0].get("data", "N/A")
        l_oper = logi.get("oper-status", [{}])[0].get("data", "N/A")

        # Notes
        note = ""
        if l_name.startswith("pp0"):
            note = "PPPoE session interface"
        elif l_name.startswith("demux0"):
            note = "Demux interface (VLAN-mapped)"
        elif l_name.startswith("et-"):
            note = "Ethernet subscriber interface"
        elif l_name.startswith("lo0"):
            note = "Loopback interface"
        elif l_name.startswith("fxp") or l_name.startswith("em"):
            note = "Management/control interface"
        elif l_name.startswith("xe"):
            note = "10G uplink interface"

        afs = logi.get("address-family", [])
        if not afs:
            organized.append({
                "Physical": p_name,
                "Logical": l_name,
                "Admin": l_admin,
                "Oper": l_oper,
                "AF": "N/A",
                "IP": "N/A",
                "Note": note or "No address family"
            })
        else:
            for af in afs:
                af_name = af.get("address-family-name", [{}])[0].get("data", "N/A")
                for addr in af.get("interface-address", []):
                    ip = addr.get("ifa-local", [{}])[0].get("data", "N/A")
                    organized.append({
                        "Physical": p_name,
                        "Logical": l_name,
                        "Admin": l_admin,
                        "Oper": l_oper,
                        "AF": af_name,
                        "IP": ip,
                        "Note": note
                    })

# === EXPORT OR PRINT ===
df = pd.DataFrame(organized)

# To print in terminal
print(df.to_string(index=False))

# Optional: export to Excel
# df.to_excel("bng_interfaces.xlsx", index=False)

