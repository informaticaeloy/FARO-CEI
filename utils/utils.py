# utils/utils.py
"""
Funciones de soporte para IPs, User-Agent, timestamps y colores.
"""
from datetime import datetime, timezone, timedelta
from flask import request
import re
import socket


def parse_user_agent(ua: str):
    """
    Devuelve (so, navegador) a partir del string completo del User-Agent.
    No depende de request.user_agent.* porque a veces devuelve None.
    """
    so = "Desconocido"
    navegador = "Desconocido"

    if not ua:
        return so, navegador

    # -------- Sistema Operativo --------
    m = re.search(r'Windows NT (\d+\.\d+)', ua, re.I)
    if m:
        nt = m.group(1)
        windows_map = {
            '10.0': 'Windows 10',
            '11.0': 'Windows 11',
            '6.3': 'Windows 8.1',
            '6.2': 'Windows 8',
            '6.1': 'Windows 7',
            '6.0': 'Windows Vista',
            '5.1': 'Windows XP',
        }
        so = windows_map.get(nt, f"Windows NT {nt}")
    elif 'Mac OS X' in ua or 'Macintosh' in ua:
        m = re.search(r'Mac OS X (\d+[_\.\d+]*)', ua)
        ver = m.group(1).replace('_', '.') if m else ''
        so = f"macOS {ver}".strip() or "macOS"
    elif 'Android' in ua:
        m = re.search(r'Android (\d+(\.\d+)*)', ua)
        ver = m.group(1) if m else ''
        so = f"Android {ver}".strip()
    elif 'iPhone' in ua or 'iPad' in ua:
        m = re.search(r'OS (\d+[_\.\d+]*)', ua)
        ver = m.group(1).replace('_', '.') if m else ''
        so = f"iOS {ver}".strip()
    elif 'Linux' in ua and 'Android' not in ua:
        so = "Linux"

    # -------- Navegador --------
    if re.search(r'Edg/\d', ua):
        m = re.search(r'Edg/(\d+(\.\d+)*)', ua)
        navegador = f"Microsoft Edge {m.group(1)}" if m else "Microsoft Edge"
    elif re.search(r'Chrome/\d', ua) and 'Chromium' not in ua:
        m = re.search(r'Chrome/(\d+(\.\d+)*)', ua)
        navegador = f"Chrome {m.group(1)}" if m else "Chrome"
    elif re.search(r'Firefox/\d', ua):
        m = re.search(r'Firefox/(\d+(\.\d+)*)', ua)
        navegador = f"Firefox {m.group(1)}" if m else "Firefox"
    elif 'Safari/' in ua and 'Chrome/' not in ua and 'Chromium/' not in ua:
        m = re.search(r'Version/(\d+(\.\d+)*)', ua)
        navegador = f"Safari {m.group(1)}" if m else "Safari"
    elif re.search(r'OPR/\d', ua) or 'Opera' in ua:
        m = re.search(r'OPR/(\d+(\.\d+)*)', ua)
        navegador = f"Opera {m.group(1)}" if m else "Opera"
    elif 'Chromium/' in ua:
        m = re.search(r'Chromium/(\d+(\.\d+)*)', ua)
        navegador = f"Chromium {m.group(1)}" if m else "Chromium"

    return so, navegador


def obtener_ip_real(req):
    """Obtiene la IP real del cliente considerando proxies y headers comunes."""
    if req.headers.get("X-Forwarded-For"):
        return req.headers.get("X-Forwarded-For").split(",")[0].strip()
    if req.headers.get("CF-Connecting-IP"):
        return req.headers.get("CF-Connecting-IP")
    if req.headers.get("X-Real-IP"):
        return req.headers.get("X-Real-IP")
    return req.remote_addr

from datetime import datetime, timedelta, timezone

from datetime import datetime, timedelta, timezone

def formatear_timestamp_es(valor_utc) -> str:
    """
    Convierte un timestamp UTC a hora local España (Madrid), con DST.
    Acepta:
        - str en formatos ISO ('YYYY-MM-DDTHH:MM:SSZ', 'YYYY-MM-DDTHH:MM:SS.ssssssZ', 'YYYY-MM-DD HH:MM:SS.ssssss')
        - datetime.datetime con tzinfo UTC o naive UTC
    """
    dt_utc = None

    # Si ya es datetime
    if isinstance(valor_utc, datetime):
        dt_utc = valor_utc
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    elif isinstance(valor_utc, str):
        formatos = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S"
        ]
        for fmt in formatos:
            try:
                dt_utc = datetime.strptime(valor_utc, fmt)
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        if not dt_utc:
            return str(valor_utc)  # No se pudo parsear
    else:
        return str(valor_utc)  # Tipo no soportado

    # Calcular DST España
    year = dt_utc.year
    march_last_sunday = max(d for d in range(31, 24, -1) if datetime(year, 3, d).weekday() == 6)
    oct_last_sunday = max(d for d in range(31, 24, -1) if datetime(year, 10, d).weekday() == 6)

    dst_start = datetime(year, 3, march_last_sunday, 2, 0, 0, tzinfo=timezone.utc)
    dst_end = datetime(year, 10, oct_last_sunday, 1, 0, 0, tzinfo=timezone.utc)

    if dst_start <= dt_utc < dst_end:
        offset = timedelta(hours=2)
        zona = "UTC+2"
    else:
        offset = timedelta(hours=1)
        zona = "UTC+1"

    dt_local = dt_utc + offset
    return dt_local.strftime(f"%d-%m-%Y %H:%M:%S {zona}")



def format_duration(seconds: int) -> str:

    """
    Convierte segundos al formato compacto:
    - '3d16h25m10s'
    - Si días y horas son 0 -> '25m10s'
    - Si minutos son 0 -> '10s'
    - Omite unidades en 0, salvo los segundos que siempre se muestran.
    """
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        s = 0

    if s < 0:
        s = 0

    days, rem = divmod(s, 86400)    # 24*60*60
    hours, rem = divmod(rem, 3600)  # 60*60
    minutes, secs = divmod(rem, 60)

    parts = []
    if days:
        parts.append(f"{days}d ")
    if hours:
        parts.append(f"{hours}h ")
    if minutes:
        parts.append(f"{minutes}m ")

    # Siempre añadimos los segundos
    parts.append(f"{secs}s")

    return "".join(parts)



# def formatear_timestamp_es(valor_utc: str) -> str:
#     """
#     Convierte un timestamp UTC a hora local España (Madrid), con horario de verano.
#     Soporta:
#         - 'YYYY-MM-DDTHH:MM:SSZ'
#         - 'YYYY-MM-DDTHH:MM:SS.ssssssZ'
#     """
#     try:
#         # Intentar con microsegundos
#         try:
#             dt_utc = datetime.strptime(valor_utc, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
#         except ValueError:
#             # Si falla, intentar sin microsegundos
#             dt_utc = datetime.strptime(valor_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#
#         # Calcular DST España (aprox.)
#         year = dt_utc.year
#         # Último domingo de marzo
#         march_last_sunday = max(d for d in range(31, 24, -1) if datetime(year, 3, d).weekday() == 6)
#         # Último domingo de octubre
#         oct_last_sunday = max(d for d in range(31, 24, -1) if datetime(year, 10, d).weekday() == 6)
#
#         dst_start = datetime(year, 3, march_last_sunday, 2, 0, 0, tzinfo=timezone.utc)
#         dst_end = datetime(year, 10, oct_last_sunday, 1, 0, 0, tzinfo=timezone.utc)
#
#         if dst_start <= dt_utc < dst_end:
#             offset = timedelta(hours=2)
#             zona = "UTC+2"
#         else:
#             offset = timedelta(hours=1)
#             zona = "UTC+1"
#
#         dt_local = dt_utc + offset
#         return dt_local.strftime(f"%d-%m-%Y %H:%M:%S {zona}")
#
#     except Exception:
#         return valor_utc

# def formatear_timestamp_es(valor_utc: str) -> str:
#     """
#     Convierte un timestamp UTC tipo 'YYYY-MM-DDTHH:MM:SSZ' a hora local España (Madrid),
#     teniendo en cuenta horario de verano.
#     """
#     try:
#         dt_utc = datetime.strptime(valor_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
#         # Cálculo DST aproximado
#         year = dt_utc.year
#         march_last_sunday = max(d for d in range(31, 24, -1) if datetime(year,3,d).weekday()==6)
#         oct_last_sunday = max(d for d in range(31,24,-1) if datetime(year,10,d).weekday()==6)
#         dst_start = datetime(year,3,march_last_sunday,2,0,0, tzinfo=timezone.utc)
#         dst_end = datetime(year,10,oct_last_sunday,1,0,0, tzinfo=timezone.utc)
#         offset = timedelta(hours=2) if dst_start <= dt_utc < dst_end else timedelta(hours=1)
#         zona = "UTC+2" if dst_start <= dt_utc < dst_end else "UTC+1"
#         dt_local = dt_utc + offset
#         return dt_local.strftime(f"%d-%m-%Y %H:%M:%S {zona}")
#     except Exception:
#         return valor_utc


def calcular_texto(color_hex: str) -> str:
    """
    Devuelve '#000000' o '#ffffff' dependiendo de la luminosidad del color de fondo.
    """
    color_hex = color_hex.lstrip("#")
    if len(color_hex) != 6:
        return "#000000"
    r,g,b = [int(color_hex[i:i+2],16) for i in (0,2,4)]
    lum = 0.2126*(r/255) + 0.7152*(g/255) + 0.0722*(b/255)
    return "#000000" if lum>0.6 else "#ffffff"


def obtener_ip_hostname():
    """
    Devuelve diccionario con IP y hostname del cliente.
    """
    ip = obtener_ip_real(request) or "Desconocida"
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = "No disponible"
    return {"hostname_local": hostname, "ip_local": ip}
