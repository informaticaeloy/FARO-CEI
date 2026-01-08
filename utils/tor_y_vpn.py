import requests
import time
import ipaddress

TOR_CACHE = {
    "ips": set(),
    "ts": 0
}
TOR_TTL = 3600  # 1 hora
TOR_EXIT_NODES = set()

VPN_KEYWORDS = (
    "amazon", "aws", "google", "azure", "ovh",
    "digitalocean", "linode", "hetzner", "vultr"
)
VPN_ASN_KEYWORDS = (
    "VPN", "HOSTING", "CLOUD", "DATACENTER", "DIGITALOCEAN",
    "AMAZON", "AWS", "AZURE", "GOOGLE", "OVH", "HETZNER"
)

def looks_like_vpn(isp: str) -> bool:
    print("*** LLEGO A LOOKS_LIKE_VPN ***")
    print(isp)
    if not isp:
        return False
    return any(k in isp.lower() for k in VPN_KEYWORDS)


def load_tor_exits():
    print("*** LLEGO A load_tor_exits ***")

    now = time.time()
    if now - TOR_CACHE["ts"] < TOR_TTL:
        return TOR_CACHE["ips"]

    ips = set()
    r = requests.get("https://check.torproject.org/exit-addresses", timeout=10)
    for line in r.text.splitlines():
        if line.startswith("ExitAddress"):
            ips.add(line.split()[1])

    TOR_CACHE["ips"] = ips
    TOR_CACHE["ts"] = now
    return ips


def is_tor(ip: str) -> bool:
    print("*** LLEGO A IS_TOR ***")
    return ip in load_tor_exits()

def analyze_ip(ip: str) -> dict:
    print("*** LLEGO A ANALYZE_IP ***")
    print(ip)
    """
    Analiza una IP y devuelve inteligencia básica:
    - TOR
    - VPN
    - ASN / Organización (si se dispone)
    """

    result = {
        "ip": ip,
        "TOR": False,
        "VPN": False,
        "asn": "",
        "org": ""
    }


    # ---------------------------
    # Validación IP
    # ---------------------------
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return result
    except Exception:
        return result

    # ---------------------------
    # Detección TOR (básica)
    # ---------------------------
    if ip in TOR_EXIT_NODES:
        result["TOR"] = True

    # ---------------------------
    # Detección VPN / Hosting
    # (por ASN / organización)
    # ---------------------------
    # Si ya tienes geoip / ASN en otro módulo,
    # aquí es donde debes integrarlo.
    try:
        from utils.geoip import geo_lookup
        geo = geo_lookup(ip)

        asn = geo.get("asn", "")
        org = geo.get("isp", "")

        result["asn"] = asn
        result["org"] = org

        org_upper = org.upper()
        if any(k in org_upper for k in VPN_ASN_KEYWORDS):
            result["VPN"] = True

    except Exception:
        pass

    return result