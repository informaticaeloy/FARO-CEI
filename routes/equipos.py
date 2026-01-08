# routes/equipos.py
from flask import Blueprint, render_template, jsonify, request, abort, redirect, url_for
import os, json
from utils.fingerprint_registry import (
    listar_fingerprints,
    cargar_fingerprint,
    eventos_por_fingerprint,
    correlacionar_fingerprints_balizas_desde_fps
)
#     correlacionar_fingerprints_balizas,
#     correlacionar_fingerprints_balizas,
from utils.auth import requiere_login
from . import FINGERPRINTS_DIR
from datetime import datetime, timezone

equipos_bp = Blueprint("equipos", __name__)

# -----------------------------
# Dashboard de equipos
# -----------------------------
@equipos_bp.route("/equipos")
def equipos_dashboard():
    if not requiere_login():
        return redirect(url_for("login"))

    fps = listar_fingerprints()
    stats = correlacionar_fingerprints_balizas_desde_fps(fps)

    equipos = []
    for fp_id, fp_data in fps.items():
        latest = fp_data.get("latest", {})
        s = stats.get(fp_id, {})

        equipos.append({
            "id": fp_id,
            "hash": latest.get("hash", {}).get("stable"),
            "timestamp": formatear_timestamp_muestreo(latest.get("timestamp")),
            "total_visitas": s.get("total_visitas", 0),
            "balizas": s.get("balizas", {}),
            "ultima_visita": s.get("ultima_visita"),
            "source": latest.get("source", {}),
            "score_vs_others": []
        })

    return render_template(
        "equipos.html",
        equipos=equipos,
        current_page="equipos"
    )

# -----------------------------
# JSON de un equipo
# -----------------------------
@equipos_bp.route("/equipos/<fingerprint_id>/json")
def equipo_fingerprint_json(fingerprint_id):
    path = os.path.join(FINGERPRINT_DIR, f"{fingerprint_id}.json")
    if not os.path.exists(path):
        abort(404)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data)

# -----------------------------
# Detalle de un equipo
# -----------------------------
@equipos_bp.route("/equipos/<fingerprint_id>")
def equipo_detalle(fingerprint_id):
    fp = cargar_fingerprint(fingerprint_id)
    if not fp:
        abort(404)

    eventos = eventos_por_fingerprint(fingerprint_id)

    return render_template(
        "equipo_detalle.html",
        equipo=fp,
        eventos=eventos
    )


def formatear_timestamp_muestreo(valor_utc: str) -> str:
    """
    Convierte un timestamp UTC ISO-8601 (con microsegundos) a formato
    'dd-mm-YYYY HH:MM:SS UTC±X' en hora local España.
    Solo para visualización.
    """
    if not valor_utc:
        return "-"

    try:
        # Ajuste para microsegundos y sufijo Z
        valor_utc = valor_utc.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(valor_utc)

        # Convertir a hora local (CET/CEST según sistema)
        dt_local = dt_utc.astimezone()

        # Calcular offset en horas
        offset_hours = int(dt_local.utcoffset().total_seconds() // 3600)
        zona = f"UTC{offset_hours:+d}"

        return dt_local.strftime(f"%d-%m-%Y %H:%M:%S {zona}")

    except Exception:
        return valor_utc