# utils/logins.py
"""
Gestión de intentos de login y control anti-bruteforce.

Funciones principales:
- log_login_attempt(): registra cada intento de login con UUID, timestamp, IP, geolocalización y OS/browser.
- cargar_login_attempts(): devuelve todos los intentos normalizados para el dashboard.
- siguiente_id_log(): calcula el siguiente ID incremental.
- check_brute_force(): detecta bloqueos por exceso de intentos.
- log_event_block(): registra eventos especiales de bloqueo.
- get_client_ip(): obtiene la IP real considerando proxies.
- parse_user_agent(): guess de OS y navegador a partir del User-Agent.
- cargar_admin(): lee el JSON de configuración de admins.
"""

import os
import json
import csv
import uuid
import ipaddress
from datetime import datetime, timedelta
from flask import request
from utils.geoip import geo_lookup
from utils.utils import parse_user_agent
#
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, "..", "data")
# ADMIN_FILE = os.path.join(DATA_DIR, "admin.json")
# LOGINS_FILE = os.path.join(DATA_DIR, "login_attempts.csv")

from . import BASE_DIR, DATA_DIR, ADMIN_FILE, LOGINS_FILE

LOG_PASSWORDS = True
FIELDNAMES = [
    "id_num", "id", "timestamp", "ip", "usuario_introducido",
    "password_introducido", "user_agent", "os", "navegador", "resultado",
    "country", "country_code", "region", "city", "lat", "lon", "isp",
    "ip_local", "hostname_local"
]

MAX_FALLOS = 5
BLOQUEO_MINUTOS = 15

# -----------------------------
# Funciones de soporte
# -----------------------------
def ensure_log_header(path=LOGINS_FILE):
    """Crea el CSV si no existe, con la cabecera."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass


def asegurar_salto_linea_csv(ruta_csv: str):
    """Garantiza que el CSV termina con un salto de línea."""
    if not os.path.exists(ruta_csv):
        return
    try:
        with open(ruta_csv, "rb") as f:
            contenido = f.read()
        if not contenido.endswith(b"\n"):
            with open(ruta_csv, "ab") as f:
                f.write(b"\n")
    except Exception:
        pass


# -----------------------------
# Funciones principales
# -----------------------------
def log_login_attempt(username: str, password: str, result: str,
                      ip_local="", hostname_local=""):
    """
    Registra un intento de login con UUID, timestamp, IP, OS, navegador y geolocalización.
    """
    ensure_log_header()
    asegurar_salto_linea_csv(LOGINS_FILE)

    intentos = cargar_login_attempts()
    id_num = siguiente_id_log(intentos)
    attempt_id = str(uuid.uuid4())
    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ip = get_client_ip()
    ua = request.headers.get("User-Agent", "")
    os_guess, browser_guess = parse_user_agent(ua)
    geo = geo_lookup(ip)

    # Detectar IP privada
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            geo.update({"country":"LAN","country_code":"LAN","region":"LAN","city":"LAN","lat":"","lon":"","isp":"LAN"})
    except ValueError:
        geo.update({"country":"","country_code":"","region":"","city":"","lat":"","lon":"","isp":""})

    pwd_to_log = password if LOG_PASSWORDS else ""

    row = {
        "id_num": id_num,
        "id": attempt_id,
        "timestamp": ts,
        "ip": ip,
        "usuario_introducido": username,
        "password_introducido": pwd_to_log,
        "user_agent": ua,
        "os": os_guess,
        "navegador": browser_guess,
        "resultado": result,
        "country": geo.get("country",""),
        "country_code": geo.get("country_code",""),
        "region": geo.get("region",""),
        "city": geo.get("city",""),
        "lat": geo.get("lat",""),
        "lon": geo.get("lon",""),
        "isp": geo.get("isp",""),
        "ip_local": ip_local,
        "hostname_local": hostname_local
    }

    with open(LOGINS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def cargar_login_attempts():
    """Carga todos los intentos normalizados para el dashboard."""
    if not os.path.exists(LOGINS_FILE):
        return []

    intentos = []
    with open(LOGINS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalización de ID
            try:
                id_num = int(row.get("id_num",""))
            except Exception:
                id_num = row.get("id_num","")
            # Normalización de timestamp
            ts_raw = row.get("timestamp","")
            fecha_str = ts_raw
            try:
                dt = datetime.fromisoformat(ts_raw.replace("Z","+00:00"))
                fecha_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
            # Normalización de resultado
            raw_res = (row.get("resultado","") or "").strip().lower()
            if raw_res in ("success","ok","true","1"):
                resultado_norm = "OK"
            elif raw_res in ("failure","failed","fail","false","0","error"):
                resultado_norm = "FAIL"
            elif raw_res in ("bloqueo","bruteforce","bloqueo bruteforce"):
                resultado_norm = "BRUTEFORCE"
            else:
                resultado_norm = "OTHER"

            intentos.append({
                "id_num": id_num,
                "timestamp": ts_raw,
                "fecha": fecha_str,
                "ip": row.get("ip",""),
                "usuario": row.get("usuario_introducido",""),
                "password": row.get("password_introducido",""),
                "user_agent": row.get("user_agent",""),
                "so": row.get("os",""),
                "navegador": row.get("navegador",""),
                "resultado": resultado_norm,
                "country": row.get("country",""),
                "country_code": row.get("country_code",""),
                "region": row.get("region",""),
                "city": row.get("city",""),
                "lat": row.get("lat",""),
                "lon": row.get("lon",""),
                "isp": row.get("isp",""),
                "ip_local": row.get("ip_local",""),
                "hostname_local": row.get("hostname_local",""),
            })
    return intentos


def siguiente_id_log(intentos):
    """Calcula el siguiente ID incremental."""
    ids_validos = []
    for e in intentos:
        if not isinstance(e, dict):
            continue
        val = e.get("id_num")
        if val is None:
            continue
        try:
            ids_validos.append(int(val))
        except ValueError:
            continue
    return max(ids_validos)+1 if ids_validos else 1


def check_brute_force(username, ip):
    """Devuelve True si se supera el límite de intentos fallidos recientes."""
    intentos = cargar_login_attempts()
    now = datetime.utcnow()
    ventana = now - timedelta(minutes=BLOQUEO_MINUTOS)
    fallos = [
        e for e in intentos
        if e["resultado"].lower() in ("fail","failure") and
           (e["usuario"]==username or e["ip"]==ip) and
           datetime.fromisoformat(e["timestamp"].replace("Z","")) > ventana
    ]
    return len(fallos) >= MAX_FALLOS


def log_event_block(username, password, ip, user_agent, os_name, navegador,
                    ip_local, hostname_local, motivo):
    """
    Registra un evento de bloqueo especial en el CSV de intentos.
    """
    asegurar_salto_linea_csv(LOGINS_FILE)
    intentos = cargar_login_attempts()
    id_num = siguiente_id_log(intentos)
    id_uuid = str(uuid.uuid4())
    dt_now = datetime.utcnow().isoformat() + "Z"

    row = {
        "id_num": id_num,
        "id": id_uuid,
        "timestamp": dt_now,
        "ip": ip_local,
        "usuario_introducido": username,
        "password_introducido": password,
        "user_agent": user_agent,
        "os": os_name,
        "navegador": "SYSTEM",
        "resultado": motivo.upper(),
        "country": "",
        "country_code": "",
        "region": "",
        "city": "",
        "lat": "",
        "lon": "",
        "isp": "",
        "ip_local": ip_local,
        "hostname_local": hostname_local,
    }

    with open(LOGINS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


# def cargar_admin():
#     """Carga el usuario admin desde JSON."""
#     if not os.path.exists(ADMIN_FILE):
#         return {"username":"admin","password":"admin"}
#     with open(ADMIN_FILE,"r",encoding="utf-8") as f:
#         return json.load(f)

def cargar_admin():
    """Devuelve un diccionario con username y password (hasheada)"""
    try:
        with open(ADMIN_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                return row
    except FileNotFoundError:
        # Si no existe, crear uno por defecto
        admin = {
            "username": "usuario",
            "password": generate_password_hash("usuario")
        }
        actualizar_password_admin(admin["password"], admin["username"])
        return admin
    return None

def get_client_ip():
    """Obtiene la IP real del cliente, considerando X-Forwarded-For."""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "N/A"

