import requests
from requests.auth import HTTPBasicAuth
from tabulate import tabulate

base_url = "http://213.133.212.24:2000"
auth = HTTPBasicAuth("support", "sabel2025!")
headers = {
    "Content-Type": "application/xml",
    "Accept": "application/json"
}
# This is stupid comment 



# STEP 1: Get all subscribers
subs_url = f"{base_url}/rpc/get-subscribers/extensive"
subs = requests.get(subs_url, headers=headers, auth=auth, timeout=60).json()

# STEP 2: Extract pp0 sessions
ppps = []
for s in subs.get("subscribers-information", [])[0].get("subscriber", []):
    iface = s.get("interface", [{}])[0].get("data", "")
    access_type = s.get("access-type", [{}])[0].get("data", "")
    if iface.startswith("pp0.") and access_type == "PPPoE":
        ppps.append((iface, s))

# STEP 3: Query and print details in tables
for pp_if, subscriber in ppps:
    print("\n" + "=" * 90)
    print(f"📡 PPP Session Interface: {pp_if}")
    print("=" * 90)

    # --- Subscriber Info ---
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

    # --- Query Detailed PPP Info ---
    url = f"{base_url}/rpc/get-ppp-interface-information/interface-name={pp_if}/extensive"
    resp = requests.get(url, headers=headers, auth=auth)
    data = resp.json()
    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])

    for s in sessions:
        def safe(key): return s.get(key, [{}])[0].get("data", "N/A")

        # Keepalive block
        ka = s.get("ppp-l2tp-session-keepalive-config", [{}])[0]
        keepalive = [
            ["Interval", ka.get("keepalive-interval", [{}])[0].get("data", "N/A")],
            ["Up Count", ka.get("keepalive-up-count", [{}])[0].get("data", "N/A")],
            ["Down Count", ka.get("keepalive-down-count", [{}])[0].get("data", "N/A")],
            ["Magic Validation", ka.get("keepalive-magic-number-validation", [{}])[0].get("data", "N/A")],
        ]

        # Protocol section
        protocol_info = []
        ip_info = []
        for section in s.get("ppp-session-protocol-information", []):
            proto = section.get("ppp-protocol", [{}])[0].get("data", "N/A")
            state = section.get("ppp-state", [{}])[0].get("data", "N/A")
            start = section.get("ppp-last-started", [{}])[0].get("data", "N/A")
            done = section.get("ppp-last-completed", [{}])[0].get("data", "N/A")
            mode = section.get("ppp-negotiation-mode", [{}])[0].get("data", "N/A")
            protocol_info.append(["Protocol", proto])
            protocol_info.append(["State", state])
            protocol_info.append(["Last Start", start])
            protocol_info.append(["Last Completed", done])
            protocol_info.append(["Negotiation Mode", mode])

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

        # Auth Info
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

        print(tabulate(keepalive, headers=["Keepalive", "Value"], tablefmt="fancy_grid"))
        print(tabulate(protocol_info, headers=["Protocol Info", "Value"], tablefmt="fancy_grid"))
        print(tabulate(ip_info, headers=["IP Assignment", "Value"], tablefmt="fancy_grid"))
        print(tabulate(auth_info, headers=["Auth Info", "Value"], tablefmt="fancy_grid"))

