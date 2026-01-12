# utils/log_login_attempt.py

import csv
import os
import uuid
import ipaddress
from datetime import datetime
from flask import request

from utils.geoip import geo_lookup  # Debe devolver dict con country, country_code, region, city, lat, lon, isp
from utils.utils import parse_user_agent

# ---------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------

from . import LOGIN_ATTEMPTS_CSV as LOG_PATH


# ⚠️ Riesgo de seguridad: solo habilitar si es estrictamente necesario
LOG_PASSWORDS = True


# ---------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------

def ensure_log_header(path: str):
    """
    Crea el fichero CSV con cabecera si no existe.
    """
    if os.path.exists(path):
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id",                   # UUID
            "timestamp",            # ISO8601 UTC
            "ip",
            "usuario_introducido",
            "password_introducido",
            "user_agent",
            "os",
            "navegador",
            "resultado",
            "country",
            "country_code",
            "region",
            "city",
            "lat",
            "lon",
            "isp"
        ])

    # Endurecimiento básico (Unix)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass





def get_client_ip():
    """
    Obtiene la IP real del cliente, respetando X-Forwarded-For.
    """
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()

    return request.remote_addr or ""


# ---------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------

def log_login_attempt(username: str, password: str, result: str):
    """
    Registra un intento de login con:
    - IP real
    - User-Agent
    - Geolocalización
    - Resultado (OK / FAIL / etc.)
    """
    ensure_log_header(LOG_PATH)

    attempt_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    ip = get_client_ip()
    ua = request.headers.get("User-Agent", "")
    os_guess, browser_guess = parse_user_agent(ua)

    # Geolocalización defensiva
    geo = geo_lookup(ip) or {}

    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            geo = {
                "country": "LAN",
                "country_code": "LAN",
                "region": "LAN",
                "city": "LAN",
                "lat": "",
                "lon": "",
                "isp": "LAN"
            }
    except ValueError:
        geo = {
            "country": "",
            "country_code": "",
            "region": "",
            "city": "",
            "lat": "",
            "lon": "",
            "isp": ""
        }

    pwd_to_log = password if LOG_PASSWORDS else ""

    row = [
        attempt_id,
        timestamp,
        ip,
        username,
        pwd_to_log,
        ua,
        os_guess,
        browser_guess,
        result,
        geo.get("country", ""),
        geo.get("country_code", ""),
        geo.get("region", ""),
        geo.get("city", ""),
        geo.get("lat", ""),
        geo.get("lon", ""),
        geo.get("isp", "")
    ]

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


