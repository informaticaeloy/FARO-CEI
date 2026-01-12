# utils/fingerprint_behavior.py

import csv
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional

from . import BALIZAS_EVENTOS_CSV, FINGERPRINT_BEHAVIOUR_CSV

# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------
def parse_ts(ts_str: str) -> Optional[datetime]:
    """Convierte timestamp ISO8601 a datetime UTC."""
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None

def to_bool(v) -> bool:
    return str(v).lower() == "true"

# -------------------------------
# Core
# -------------------------------
def calculate_behavior(force: bool = False, max_age_minutes: int = 5):
    """
    Calcula métricas de comportamiento por fingerprint.
    TOR/VPN se calculan de forma estable por IP pública / ISP único.
    Devuelve lista de dicts y timestamp de cálculo.
    """
    now = datetime.now(timezone.utc)

    # Reusar CSV si es reciente
    if not force and os.path.exists(FINGERPRINT_BEHAVIOUR_CSV):
        mtime = datetime.fromtimestamp(os.path.getmtime(FINGERPRINT_BEHAVIOUR_CSV), timezone.utc)
        if (now - mtime).total_seconds() / 60 < max_age_minutes:
            with open(FINGERPRINT_BEHAVIOUR_CSV, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f)), mtime

    # Cargar eventos
    events = defaultdict(list)
    if os.path.exists(BALIZAS_EVENTOS_CSV):
        with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                fp = row.get("fingerprint_id")
                if not fp:
                    continue
                ts = parse_ts(row.get("timestamp", ""))
                if not ts:
                    continue
                events[fp].append({
                    "baliza": row.get("payload") or row.get("origen", "UNKNOWN"),
                    "ts": ts,
                    "flag_tor": to_bool(row.get("flag_tor")),
                    "flag_vpn": to_bool(row.get("flag_vpn"))
                })

    # Analizar por fingerprint
    results = []
    for fp, ev_list in events.items():
        visitas = len(ev_list)
        balizas = len({e["baliza"] for e in ev_list})
        window_sec = int((max(e["ts"] for e in ev_list) - min(e["ts"] for e in ev_list)).total_seconds())
        base_score = min(100, window_sec // 120 + visitas * 5)

        # Conteo TOR/VPN
        tor_visitas = sum(1 for e in ev_list if e["flag_tor"])
        vpn_visitas = sum(1 for e in ev_list if e["flag_vpn"])
        total_visitas = visitas

        tor_flag = tor_visitas > 0
        vpn_flag = vpn_visitas > 0

        tor_summary = f"YES {tor_visitas}/{total_visitas}" if tor_flag else f"NO 0/{total_visitas}"
        vpn_summary = f"YES {vpn_visitas}/{total_visitas}" if vpn_flag else f"NO 0/{total_visitas}"

        # Ajuste de score
        score = base_score
        if tor_flag:
            score = 100
        elif vpn_flag and base_score >= 60:
            score = min(100, base_score + 20)

        # Clasificación
        if score < 50:
            classification = "LEGIT"
        elif score < 80:
            classification = "SUSPICIOUS"
        else:
            classification = "MALICIOUS"

        results.append({
            "fingerprint": fp,
            "TOR": tor_summary,
            "VPN": vpn_summary,
            "Visitas": visitas,
            "Balizas": balizas,
            "Ventana (s)": window_sec,
            "Score": score,
            "Clasificación": classification
        })

    # Guardar CSV
    if results:
        with open(FINGERPRINT_BEHAVIOUR_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    return results, now



def is_public_ip(ip_str: str) -> bool:
    try:
        ip = ip_address(ip_str)
        return not ip.is_private and not ip.is_loopback and not ip.is_reserved
    except ValueError:
        return False




# def calculate_behavior(force: bool = False, max_age_minutes: int = 5) -> Tuple[List[Dict], datetime]:
#     """
#     Calcula métricas de comportamiento por fingerprint.
#
#     Clasificación:
#         - LEGIT
#         - SUSPICIOUS
#         - MALICIOUS
#     """
#     now = datetime.now(timezone.utc)
#
#     # -----------------------------------------------------
#     # Reutilizar CSV si es reciente
#     # -----------------------------------------------------
#     if not force and os.path.exists(FINGERPRINT_BEHAVIOUR_CSV):
#         mtime = datetime.fromtimestamp(os.path.getmtime(FINGERPRINT_BEHAVIOUR_CSV), timezone.utc)
#         age_min = (now - mtime).total_seconds() / 60
#         if age_min < max_age_minutes:
#             results = []
#             with open(FINGERPRINT_BEHAVIOUR_CSV, newline="", encoding="utf-8") as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     results.append(row)
#             return results, mtime
#
#     # -----------------------------------------------------
#     # Cargar eventos desde balizas_eventos.csv
#     # -----------------------------------------------------
#     events: Dict[str, List[Dict]] = defaultdict(list)
#
#     if os.path.exists(BALIZAS_EVENTOS_CSV):
#         with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 fingerprint = row.get("fingerprint_id")
#                 if not fingerprint:
#                     continue
#
#                 ts = parse_ts(row.get("timestamp", ""))
#                 if not ts:
#                     continue
#
#                 events[fingerprint].append({
#                     "baliza": row.get("payload") or row.get("origen", "UNKNOWN"),
#                     "ts": ts,
#                     "ip": row.get("ip"),
#                     "isp": row.get("isp", "")
#                 })
#
#     # -----------------------------------------------------
#     # Análisis por fingerprint
#     # -----------------------------------------------------
#     results: List[Dict] = []
#
#     for fp, ev_list in events.items():
#         if not ev_list:
#             continue
#
#         visitas = len(ev_list)
#         balizas = len(set(e["baliza"] for e in ev_list))
#
#         window_sec = int(
#             (max(e["ts"] for e in ev_list) - min(e["ts"] for e in ev_list)).total_seconds()
#         )
#
#         # -----------------------------
#         # Score base (temporal + volumen)
#         # -----------------------------
#         score = min(100, window_sec // 120 + visitas * 5)
#
#         # -----------------------------
#         # TOR / VPN detection
#         # -----------------------------
#         ips = {e["ip"] for e in ev_list if e.get("ip")}
#         isps = {e["isp"] for e in ev_list if e.get("isp")}
#
#         tor_flag = any(is_tor(ip) for ip in ips if ip)
#         vpn_flag = any(looks_like_vpn(isp) for isp in isps if isp)
#
#         adjusted_score = score
#
#         if tor_flag:
#             adjusted_score = 100
#         elif vpn_flag and score >= 60:
#             adjusted_score = min(100, score + 20)
#
#         # -----------------------------
#         # Clasificación final
#         # -----------------------------
#         if adjusted_score < 50:
#             classification = "LEGIT"
#         elif adjusted_score < 80:
#             classification = "SUSPICIOUS"
#         else:
#             classification = "MALICIOUS"
#
#         results.append({
#             "fingerprint": fp,
#             "TOR": tor_flag,
#             "VPN": vpn_flag,
#             "Visitas": visitas,
#             "Balizas": balizas,
#             "Ventana (s)": window_sec,
#             "Score": adjusted_score,
#             "Clasificación": classification
#         })
#
#     # -----------------------------------------------------
#     # Persistencia
#     # -----------------------------------------------------
#     if results:
#         with open(FINGERPRINT_BEHAVIOUR_CSV, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
#             writer.writeheader()
#             writer.writerows(results)
#
#     return results, now

# import csv
# import os
# from collections import defaultdict
# from datetime import datetime, timezone
# from typing import List, Dict, Tuple, Optional
# from utils.tor_y_vpn import *
#
#
# from . import BASE_DIR, BALIZAS_EVENTOS_CSV, FINGERPRINT_BEHAVIOUR_CSV
#
# def parse_ts(ts_str: str) -> Optional[datetime]:
#     """
#     Convierte un timestamp ISO8601 tipo '2025-12-04T09:41:55Z' a datetime con timezone UTC.
#     Devuelve None si no puede parsearlo.
#     """
#     try:
#         return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
#     except Exception:
#         return None
#
#
# def calculate_behavior(force: bool = False, max_age_minutes: int = 5) -> Tuple[List[Dict], datetime]:
#     """
#     Calcula métricas de comportamiento por fingerprint.
#
#     Parámetros:
#         force: recalcular aunque exista FINGERPRINT_BEHAVIOUR_CSV reciente.
#         max_age_minutes: tiempo en minutos para considerar FINGERPRINT_BEHAVIOUR_CSV reciente.
#
#     Devuelve:
#         results: lista de dicts con métricas de cada fingerprint
#         timestamp: datetime de la última generación
#     """
#     now = datetime.now(timezone.utc)
#
#     # Usar CSV existente si es reciente
#     if not force and os.path.exists(FINGERPRINT_BEHAVIOUR_CSV):
#         mtime = datetime.fromtimestamp(os.path.getmtime(FINGERPRINT_BEHAVIOUR_CSV), timezone.utc)
#         age_min = (now - mtime).total_seconds() / 60
#         if age_min < max_age_minutes:
#             results = []
#             with open(FINGERPRINT_BEHAVIOUR_CSV, newline="", encoding="utf-8") as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     results.append(row)
#             return results, mtime
#
#     # Recalcular desde balizas_eventos.csv
#     events: Dict[str, List[Dict]] = defaultdict(list)
#     if os.path.exists(BALIZAS_EVENTOS_CSV):
#         with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 fingerprint = row.get("fingerprint_id")
#                 if not fingerprint:
#                     continue
#                 ts = parse_ts(row["timestamp"])
#                 if ts is None:
#                     continue
#                 events[fingerprint].append({
#                     "baliza": row.get("origen", "UNKNOWN"),
#                     "ts": ts
#                 })
#
#     results: List[Dict] = []
#     for fp, ev_list in events.items():
#         if not ev_list:
#             continue
#         visitas = len(ev_list)
#         balizas = len(set(e["baliza"] for e in ev_list))
#
#         window_sec = int(
#             (max(e["ts"] for e in ev_list) - min(e["ts"] for e in ev_list)).total_seconds()
#         )
#
#         score = min(100, window_sec // 120 + visitas * 5)
#
#         if score < 50:
#             classification = "LEGIT"
#         elif score < 80:
#             classification = "SUSPICIOUS"
#         else:
#             classification = "MALICIOUS"
#
#         results.append({
#             "fingerprint": fp,
#             "TOR": False,
#             "Visitas": visitas,
#             "Balizas": balizas,
#             "Ventana (s)": window_sec,
#             "Score": score,
#             "Clasificación": classification
#         })
#
#     # Guardar CSV
#     if results:
#         with open(FINGERPRINT_BEHAVIOUR_CSV, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
#             writer.writeheader()
#             writer.writerows(results)
#
#     return results, now
#
#
# # if __name__ == "__main__":
# #     # Ejecución directa para pruebas
# #     data, ts = calculate_behavior()
# #     for r in data:
# #         print(r)
# #     print(f"[OK] Resultado exportado a: {FINGERPRINT_BEHAVIOUR_CSV} (generado: {ts.isoformat()})")
