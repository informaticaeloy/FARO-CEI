# utils/geoip.py
"""
Módulo para consultas geográficas de IP (GeoIP) y conversión de códigos de país a emoji.
Incluye:
- cache local de resultados para no sobrecargar la API
- tratamiento de IPs locales y LAN
- conversión de ISO2 country codes a emojis
"""

import os
import json
import requests
from pathlib import Path
from time import sleep

# Carpeta para guardar caché de IPs
from . import GEOIP_CACHE_FILE as CACHE_FILE

# Cargar caché si existe
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        GEOIP_CACHE = json.load(f)
else:
    GEOIP_CACHE = {}

API_URL = "http://ip-api.com/json/{ip}"  # API gratuita

# ---------------------------
# Funciones
# ---------------------------
def save_cache():
    """Guardar la caché de IPs en disco"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(GEOIP_CACHE, f, indent=2, ensure_ascii=False)


def geo_lookup(ip: str) -> dict:
    """
    Devuelve información geográfica de una IP.
    - Usa cache local si disponible.
    - Trata IPs locales (LAN, localhost) de manera especial.
    - Consulta la API externa si no está en cache.

    Args:
        ip (str): Dirección IP a consultar

    Returns:
        dict: Diccionario con keys: ip, country, country_code, region, city, lat, lon, isp
    """
    ip = ip.strip()
    if ip in GEOIP_CACHE:
        return GEOIP_CACHE[ip]

    result = {"ip": ip, "country": "", "country_code": "", "region": "", "city": "", "lat": None, "lon": None, "isp": ""}

    # IP local -> LAN
    if ip.startswith(("192.", "10.", "172.")):
        result.update({
            "country": "LAN",
            "country_code": "LAN",
            "region": "LAN",
            "city": "LAN",
            "lat": 0,
            "lon": 0,
            "isp": "LAN",
        })
    elif ip.startswith("127."):
        result.update({
            "country": "Localhost",
            "country_code": "localhost",
            "region": "localhost",
            "city": "localhost",
            "lat": 0,
            "lon": 0,
            "isp": "localhost",
        })
    else:
        try:
            resp = requests.get(API_URL.format(ip=ip), timeout=5)
            data = resp.json()
            if data.get("status") == "success":
                result.update({
                    "country": data.get("country", ""),
                    "country_code": data.get("countryCode", ""),
                    "region": data.get("regionName", ""),
                    "city": data.get("city", ""),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "isp": data.get("isp", ""),
                })
        except Exception as e:
            print(f"[geoip] Error consultando IP {ip}: {e}")

    GEOIP_CACHE[ip] = result
    save_cache()
    sleep(0.5)
    return result


def country_code_to_emoji(code: str) -> str:
    """
    Convierte un código de país ISO2 (ej. 'ES', 'US') a emoji de bandera.

    Args:
        code (str): Código de país ISO2

    Returns:
        str: Emoji correspondiente o cadena vacía si inválido
    """
    if not code or len(code) != 2:
        return ""
    code = code.upper()
    OFFSET = 127397
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)

