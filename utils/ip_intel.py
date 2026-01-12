# utils/ip_intel.py

import socket
import ipaddress

def is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except Exception:
        return False


def enrich_ip(ip: str) -> dict:
    if is_private_ip(ip):
        return {
            "ip": ip,
            "scope": "PRIVATE",
            "asn": "N/A",
            "org": "Internal"
        }

    return {
        "ip": ip,
        "scope": "PUBLIC",
        "asn": "UNKNOWN",
        "org": "UNKNOWN"
    }
