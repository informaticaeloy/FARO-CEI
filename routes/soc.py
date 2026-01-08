# routes/soc.py
# =====================================
# Blueprint SOC
# =====================================

import os
import csv
import json
from flask import Blueprint, render_template, jsonify

from datetime import datetime, timezone, timedelta

from utils.auth import requiere_login
from utils.utils import formatear_timestamp_es
from soc.behavior import soc_behavior_handler
from utils.fingerprint_behavior import calculate_behavior

from . import BALIZAS_EVENTOS_CSV, FINGERPRINT_EVENTS_CSV

soc_bp = Blueprint("soc", __name__)

# -------------------------------------------------
# Endpoint SOC (API)
# -------------------------------------------------
@soc_bp.route("/soc/behavior", methods=["GET"])
def soc_behavior():
    if not requiere_login():
        return "", 401

    return soc_behavior_handler()


# -------------------------------------------------
# Vista SOC Behavior
# -------------------------------------------------
@soc_bp.route("/soc/behavior/view", methods=["GET"])
def soc_behavior_view():
    if not requiere_login():
        return "", 401

    data, last_calc = calculate_behavior()
    last_calc_str = last_calc.strftime("%Y-%m-%d %H:%M:%S UTC")

    return render_template(
        "soc_behavior.html",
        data=data,
        last_calc=last_calc_str,
        current_page="soc"
    )


# -------------------------------------------------
# Refresh manual SOC Behavior
# -------------------------------------------------
@soc_bp.route("/soc/behavior/refresh", methods=["POST"])
def soc_behavior_refresh():
    if not requiere_login():
        return "", 401

    _, last_calc = calculate_behavior(force=True)
    last_calc_str = last_calc.strftime("%Y-%m-%d %H:%M:%S UTC")

    return jsonify({
        "timestamp": last_calc_str
    })




@soc_bp.route("/soc/fingerprint/<fp_id>", methods=["GET"])
def soc_fingerprint_view(fp_id):
    if not requiere_login():
        return "", 401

    timeline = []
    ip_stats = {}
    tor = False
    vpn = False
    dt_list = []  # Para calcular ventana en segundos correctamente

    if os.path.exists(BALIZAS_EVENTOS_CSV):
        with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("fingerprint_id") != fp_id:
                    continue

                ip = row.get("ip", "").strip()
                isp = (row.get("isp") or "").strip().upper()
                tor_flag = _to_bool(row.get("flag_tor"))
                vpn_flag = _to_bool(row.get("flag_vpn"))

                tor |= tor_flag
                vpn |= vpn_flag

                ip_stats.setdefault(ip, {
                    "count": 0,
                    "asn": row.get("asn"),
                    "org": isp,
                    "TOR": False,
                    "VPN": False
                })
                ip_stats[ip]["count"] += 1
                ip_stats[ip]["TOR"] |= tor_flag
                ip_stats[ip]["VPN"] |= vpn_flag

                # Parse timestamp UTC para cálculo
                ts_obj = None
                if row.get("timestamp"):
                    try:
                        ts_obj = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                        dt_list.append(ts_obj)
                    except Exception:
                        ts_obj = None

                timeline.append({
                    "timestamp": formatear_timestamp_es(row.get("timestamp")) if row.get("timestamp") else "N/A",
                    "ts_obj": ts_obj,  # Guardamos datetime para cálculo
                    "baliza": row.get("payload") or row.get("origen"),
                    "ip": ip,
                    "asn": row.get("asn"),
                    "org": isp,
                    "TOR": tor_flag,
                    "VPN": vpn_flag,
                    "user_agent": row.get("user_agent")
                })

    timeline.sort(key=lambda x: x["ts_obj"] or datetime.min, reverse=True)

    total_visitas = len(timeline)
    total_balizas = len({e["baliza"] for e in timeline})

    ventana_s = 0
    if dt_list:
        ventana_s = int((max(dt_list) - min(dt_list)).total_seconds())

    # Score
    score = min(100, ventana_s // 120 + total_visitas * 5)
    if tor:
        score = 100
    elif vpn and score >= 60:
        score = min(100, score + 20)

    if score < 50:
        clasificacion = "LEGIT"
    elif score < 80:
        clasificacion = "SUSPICIOUS"
    else:
        clasificacion = "MALICIOUS"

    return render_template(
        "soc_fingerprint.html",
        fp_id=fp_id,
        events=timeline,
        ip_stats=ip_stats,
        tor=tor,
        vpn=vpn,
        total_visitas=total_visitas,
        total_balizas=total_balizas,
        ventana_s=ventana_s,
        score=score,
        clasificacion=clasificacion,
        current_page="soc"
    )


# @soc_bp.route("/soc/fingerprint/<fp_id>", methods=["GET"])
# def soc_fingerprint_view(fp_id):
#     if not requiere_login():
#         return "", 401
#
#     timeline = []
#     ip_stats = {}
#     tor = False
#     vpn = False
#
#     if os.path.exists(BALIZAS_EVENTOS_CSV):
#         with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 if row.get("fingerprint_id") != fp_id:
#                     continue
#
#                 ip = row.get("ip", "").strip()
#                 isp = (row.get("isp") or "").strip().upper()
#                 tor_flag = _to_bool(row.get("flag_tor"))
#                 vpn_flag = _to_bool(row.get("flag_vpn"))
#
#                 tor |= tor_flag
#                 vpn |= vpn_flag
#
#                 ip_stats.setdefault(ip, {
#                     "count": 0,
#                     "asn": row.get("asn"),
#                     "org": isp,
#                     "TOR": False,
#                     "VPN": False
#                 })
#                 ip_stats[ip]["count"] += 1
#                 ip_stats[ip]["TOR"] |= tor_flag
#                 ip_stats[ip]["VPN"] |= vpn_flag
#
#                 timeline.append({
#                     "timestamp": formatear_timestamp_es(row.get("timestamp")) if row.get("timestamp") else "N/A",
#                     "baliza": row.get("payload") or row.get("origen"),
#                     "ip": ip,
#                     "asn": row.get("asn"),
#                     "org": isp,
#                     "TOR": tor_flag,
#                     "VPN": vpn_flag,
#                     "user_agent": row.get("user_agent")
#                 })
#
#     timeline.sort(key=lambda x: x["timestamp"], reverse=True)
#
#     total_visitas = len(timeline)
#     total_balizas = len({e["baliza"] for e in timeline})
#
#     ventana_s = 0
#     if timeline:
#         ts_list = []
#         for e in timeline:
#             try:
#                 dt = datetime.strptime(e["timestamp"][:19], "%d-%m-%Y %H:%M:%S")  # Ignorar zona
#                 ts_list.append(dt)
#             except Exception:
#                 continue
#         if ts_list:
#             ventana_s = int((max(ts_list) - min(ts_list)).total_seconds())
#
#     score = min(100, ventana_s // 120 + total_visitas * 5)
#     if tor:
#         score = 100
#     elif vpn and score >= 60:
#         score = min(100, score + 20)
#
#     if score < 50:
#         clasificacion = "LEGIT"
#     elif score < 80:
#         clasificacion = "SUSPICIOUS"
#     else:
#         clasificacion = "MALICIOUS"
#
#     return render_template(
#         "soc_fingerprint.html",
#         fp_id=fp_id,
#         events=timeline,
#         ip_stats=ip_stats,
#         tor=tor,
#         vpn=vpn,
#         total_visitas=total_visitas,
#         total_balizas=total_balizas,
#         ventana_s=ventana_s,
#         score=score,
#         clasificacion=clasificacion,
#         current_page="soc"
#     )


# @soc_bp.route("/soc/fingerprint/<fp_id>", methods=["GET"])
# def soc_fingerprint_view(fp_id):
#     if not requiere_login():
#         return "", 401
#
#     #from utils.eventos import get_fingerprint_flags
#
#     timeline = []
#     ip_stats = {}
#     tor = False
#     vpn = False
#
#     # -------------------------------------------------
#     # Timeline SOLO con datos persistidos
#     # -------------------------------------------------
#     if os.path.exists(BALIZAS_EVENTOS_CSV):
#         with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
#             for row in csv.DictReader(f):
#                 if row.get("fingerprint_id") != fp_id:
#                     continue
#
#                 ip = row.get("ip", "").strip()
#                 isp = (row.get("isp") or "").strip().upper()
#
#                 # Obtener TOR/VPN determinista por fingerprint
#                 tor_flag = _to_bool(row.get("flag_tor"))
#                 vpn_flag = _to_bool(row.get("flag_vpn"))
#
#                 tor |= tor_flag
#                 vpn |= vpn_flag
#
#                 # tor_flag, vpn_flag = get_fingerprint_flags(fp_id, tor=row.get("TOR"), vpn=row.get("VPN"))
#                 # tor |= tor_flag
#                 # vpn |= vpn_flag
#
#                 ip_stats.setdefault(ip, {
#                     "count": 0,
#                     "asn": row.get("asn"),
#                     "org": isp,
#                     "TOR": False,
#                     "VPN": False
#                 })
#                 ip_stats[ip]["count"] += 1
#                 ip_stats[ip]["TOR"] |= tor_flag
#                 ip_stats[ip]["VPN"] |= vpn_flag
#
#                 timeline.append({
#                     "timestamp": row.get("timestamp"),
#                     "baliza": row.get("payload") or row.get("origen"),
#                     "ip": ip,
#                     "asn": row.get("asn"),
#                     "org": isp,
#                     "TOR": tor_flag,
#                     "VPN": vpn_flag,
#                     "user_agent": row.get("ua")
#                 })
#
#     timeline.sort(key=lambda x: x["timestamp"], reverse=True)
#
#     return render_template(
#         "soc_fingerprint.html",
#         fp_id=fp_id,
#         timeline=timeline,
#         ip_stats=ip_stats,
#         tor=tor,
#         vpn=vpn,
#         current_page="soc"
#     )





@soc_bp.route("/soc/fingerprint/<fp_id>/timeline")
def soc_fingerprint_timeline(fp_id):
    events = []
    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("fingerprint_id") == fp_id:
                events.append(row)

    events.sort(key=lambda x: x["timestamp"])

    return render_template(
        "soc_fingerprint_timeline.html",
        fingerprint=fp_id,
        events=events
    )


@soc_bp.route("/soc/fingerprint/<fp_id>/network")
def soc_fingerprint_network(fp_id):
    ips = set()

    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("fingerprint_id") == fp_id:
                if row.get("ip"):
                    ips.add(row["ip"])

    enriched = [enrich_ip(ip) for ip in ips]

    return render_template(
        "soc_fingerprint_network.html",
        fingerprint=fp_id,
        ips=enriched
    )

def _to_bool(v):
    return str(v).lower() == "true"


# @soc_bp.route("/soc/fingerprint/<fp_id>", methods=["GET"])
# def soc_fingerprint_view(fp_id):
#     if not requiere_login():
#         return "", 401
#
#     events = []
#
#     if os.path.exists(FINGERPRINT_EVENTS_CSV):
#         with open(FINGERPRINT_EVENTS_CSV, newline="", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 if row.get("fp_id") == fp_id:
#                     events.append({
#                         "timestamp": row.get("timestamp"),
#                         "baliza_id": row.get("baliza_id"),
#                         "confidence": float(row.get("confidence", 0)),
#                         "engines": json.loads(row.get("engines", "{}")),
#                         "user_agent": row.get("ua"),
#                         "timezone": row.get("timezone"),
#                         "screen": row.get("screen"),
#                         "platform": row.get("platform")
#                     })
#
#     events.sort(key=lambda x: x["timestamp"], reverse=True)
#
#     return render_template(
#         "soc_fingerprint.html",
#         fp_id=fp_id,
#         events=events,
#         current_page="soc"
#     )

# # ---------------------------
# # Endpoint SOC
# # ---------------------------
# @app.route("/soc/behavior", methods=["GET"])
# def soc_behavior():
#     return soc_behavior_handler()
#
# @app.route("/soc/behavior/view")
# def soc_behavior_view_route():
#     """Cálculo automático si CSV es viejo, renderiza tabla."""
#     data, last_calc = calculate_behavior()
#     last_calc_str = last_calc.strftime("%Y-%m-%d %H:%M:%S UTC")
#     return render_template("soc_behavior.html", data=data, last_calc=last_calc_str)
#
# @app.route("/soc/behavior/refresh", methods=["POST"])
# def soc_behavior_refresh():
#     """Fuerza el cálculo manual desde el botón."""
#     data, last_calc = calculate_behavior(force=True)
#     last_calc_str = last_calc.strftime("%Y-%m-%d %H:%M:%S UTC")
#     return jsonify({"timestamp": last_calc_str})
# # @app.route("/soc/behavior/view")
# # def soc_behavior_view_route():
# #     return soc_behavior_view()
#
# @app.route("/soc/fingerprint/<fp_id>")
# def soc_fingerprint_view(fp_id):
#     events = []
#
#     if os.path.exists(FINGERPRINT_EVENTS_CSV):
#         with open(FINGERPRINT_EVENTS_CSV, newline="", encoding="utf-8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 if row["fp_id"] == fp_id:
#                     events.append({
#                         "timestamp": row["timestamp"],
#                         "baliza_id": row["baliza_id"],
#                         "confidence": float(row["confidence"]),
#                         "engines": json.loads(row["engines"]),
#                         "user_agent": row.get("ua"),
#                         "timezone": row.get("timezone"),
#                         "screen": row.get("screen"),
#                         "platform": row.get("platform")
#                     })
#
#     events.sort(key=lambda x: x["timestamp"], reverse=True)
#
#     return render_template(
#         "soc_fingerprint.html",
#         fp_id=fp_id,
#         events=events
#     )
