# utils/eventos.py
"""
Módulo para gestión de eventos en CSV.

Funciones principales:
- cargar_eventos(): devuelve todos los eventos como lista de diccionarios.
- guardar_eventos(eventos): sobrescribe el CSV con los eventos dados.
- siguiente_id(eventos): calcula el siguiente ID incremental para un nuevo evento.
"""

import os
import csv

from . import BASE_DIR, EVENTOS_CSV


# Claves estandar para los eventos
# EVENT_KEYS = [
#     "id_num", "timestamp", "ip", "tipo", "evento", "origen", "payload",
#     "so", "navegador", "user_agent", "country", "country_code",
#     "region", "city", "lat", "lon", "isp", "ip_local", "hostname_local", "fingerprint_id", "flag_tor", "flag_vpn"
# ]

def cargar_eventos():
    """
    Carga todos los eventos desde el CSV.

    Returns:
        list[dict]: Lista de eventos, vacía si el CSV no existe.
    """
    if not os.path.exists(EVENTOS_CSV):
        return []

    eventos = []
    try:
        with open(EVENTOS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                eventos.append({
                    "id_num": int(row["id_num"]),
                    "timestamp": row["timestamp"],
                    "ip": row["ip"],
                    "tipo": row["tipo"],
                    "evento": row["evento"],
                    "origen": row["origen"],
                    "payload": row["payload"],
                    "so": row["so"],
                    "navegador": row["navegador"],
                    "user_agent": row["user_agent"],
                    "country": row["country"],
                    "country_code": row["country_code"],
                    "region": row["region"],
                    "city": row["city"],
                    "lat": row["lat"],
                    "lon": row["lon"],
                    "isp": row["isp"],
                    "ip_local": row["ip_local"],
                    "hostname_local": row["hostname_local"],
                    "fingerprint_id": row["fingerprint_id"],
                    "flag_tor": str(row.get("flag_tor")).lower() == "true",
                    "flag_vpn": str(row.get("flag_vpn")).lower() == "true"

                    # "flag_tor": analyze_ip(row["ip"])["TOR"],
                    # "flag_vpn": analyze_ip(row["ip"])["VPN"]
                })
    except Exception as e:
        print(f"[eventos] Error al cargar eventos: {e}")
        return []

    return eventos





def siguiente_id(eventos):
    """
    Calcula el siguiente ID incremental para un nuevo evento.

    Args:
        eventos (list[dict]): Lista de eventos existentes

    Returns:
        int: Siguiente ID numérico
    """
    if not eventos:
        return 1
    return max(e["id_num"] for e in eventos) + 1


def guardar_evento(evento: dict):
    """
    Añade un evento al CSV con normalización estricta
    para garantizar cálculos SOC deterministas.
    """

    ensure_eventos_header()

    # -----------------------------
    # Normalización SOC
    # -----------------------------
    evento = evento.copy()

    # IP
    evento["ip"] = (evento.get("ip") or "").strip()

    # ISP: normalizar para detección estable
    isp = (evento.get("isp") or "").strip()
    if not isp or isp.lower() in ("unknown", "n/a", "-"):
        isp = ""
    evento["isp"] = isp.upper()   # CLAVE: mismo ISP => mismo string

    # Fingerprint
    evento["fingerprint_id"] = (evento.get("fingerprint_id") or "").strip()

    # Payload / origen
    evento["payload"] = (evento.get("payload") or "").strip()
    evento["origen"] = (evento.get("origen") or "").strip()

    # -----------------------------
    # TOR / VPN (ya calculado en origen)
    # -----------------------------
    evento["flag_tor"] = bool(evento.get("flag_tor", False))
    evento["flag_vpn"] = bool(evento.get("flag_vpn", False))

    with open(EVENTOS_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id_num", "timestamp", "ip", "tipo", "evento", "origen",
            "payload", "so", "navegador", "user_agent",
            "country", "country_code", "region", "city", "lat", "lon", "isp",
            "ip_local", "hostname_local", "fingerprint_id", "flag_tor", "flag_vpn"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(evento)



def ensure_eventos_header():
    """Crea la cabecera de CSV de eventos si no existe."""
    if not os.path.exists(EVENTOS_CSV) or os.path.getsize(EVENTOS_CSV) == 0:
        with open(EVENTOS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id_num", "timestamp", "ip", "tipo", "evento", "origen",
                "payload", "so", "navegador", "user_agent",
                "country", "country_code", "region", "city", "lat", "lon", "isp",
                "ip_local", "hostname_local", "fingerprint_id", "flag_tor", "flag_vpn"
            ])


# Al inicio del archivo, tras imports
#FINGERPRINT_CACHE = {}  # fingerprint_id -> {"TOR": bool, "VPN": bool}

# def get_fingerprint_flags(fingerprint_id, tor=None, vpn=None):
#     """
#     Obtiene los flags TOR/VPN de un fingerprint de forma determinista.
#     Si ya existen en cache, los devuelve.
#     Si no existen, los almacena usando los valores pasados.
#     """
#     if not fingerprint_id:
#         return False, False
#
#     if fingerprint_id in FINGERPRINT_CACHE:
#         cached = FINGERPRINT_CACHE[fingerprint_id]
#         return cached["TOR"], cached["VPN"]
#
#     # Si no hay cache, guardar los valores que vienen
#     FINGERPRINT_CACHE[fingerprint_id] = {
#         "TOR": bool(tor),
#         "VPN": bool(vpn)
#     }
#     return bool(tor), bool(vpn)

