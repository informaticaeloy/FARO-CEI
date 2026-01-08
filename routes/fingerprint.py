# routes/fingerprint.py

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import json
from utils.fingerprint import guardar_fingerprint
from utils.eventos import cargar_eventos, guardar_evento, siguiente_id
from utils.utils import obtener_ip_hostname, obtener_ip_real, parse_user_agent
from utils.geoip import geo_lookup

fingerprint_bp = Blueprint("fingerprint", __name__)

# -----------------------------------------------------------------
# FINGERPRINT · ENDPOINT ÚNICO DE INGESTA
# -----------------------------------------------------------------
@fingerprint_bp.route("/fingerprint/collect", methods=["POST"])
def fingerprint_collect():
    print("[DEBUG] /fingerprint/collect llamada")  # <-- print inicial
    """
    Endpoint corporativo de ingesta de fingerprints.
    Centraliza la recepción y delega el procesado según source_type.
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return {"status": "error", "msg": "invalid json"}, 400

    if not data or "fingerprint" not in data:
        return {"status": "error", "msg": "missing fingerprint"}, 400

    source_type = data.get("source_type", "unknown")
    origen = data.get("origen")
    fingerprint = data.get("fingerprint", {})
    fingerprint_id = fingerprint.get("engines", {}).get("fingerprintjs", {}).get("data", {}).get("visitorId", "N/A")
    # print(f">>> FINGERPRINT_ID {fingerprint_id}")
    profile = data.get("profile", "default")


    return jsonify({"status": "ok", "fingerprint_id": fingerprint_id})


# -----------------------------------------------------------------
# FINGERPRINT · RUTA ESPECÍFICA BALIZA HTML
# -----------------------------------------------------------------
@fingerprint_bp.route("/fingerprint/collect_baliza", methods=["POST"])
def collect_fingerprint_baliza():
    # print("[DEBUG] /fingerprint/collect_baliza llamada")  # <-- print inicial

    """
    Endpoint especializado para balizas HTML.
    - Reutiliza o crea fingerprint
    - Registra evento VIEW
    - Enlaza fingerprint ↔ evento
    """

    # 2. Capturar datos del request
    if request.method == "POST":
        try:
            data = request.get_json(silent=True) or request.form.to_dict()
        except Exception:
            return {"status": "error", "msg": "invalid json"}, 400
    else:
        data = request.args.to_dict()

    payload = json.dumps(data, ensure_ascii=False)

    # 3. Evento y origen
    evento_val = data.get("evento") or data.get("e") or "Evento genérico"
    origen_val = data.get("origen") or data.get("o") or "Sistema"

    # 4. Tipo derivado automáticamente
    ev_upper = evento_val.upper()
    tipo_val = ("ERROR" if ev_upper in ("ERROR","FALLO","ALERTA")
                else "WARN" if ev_upper in ("WARN","AVISO")
                else "INFO" if ev_upper in ("INFO","CHECK","OK")
                else "EVENT")

    # 5. Host local
    host_info = obtener_ip_hostname()
    ip_local = host_info["ip_local"]
    hostname_local = host_info["hostname_local"]

    # 6. User agent y sistema/navegador
    ua_str = request.user_agent.string or ""
    so, nav = parse_user_agent(ua_str)

    # 7. IP real y geolocalización
    ip_real = obtener_ip_real(request) or "N/A"
    geo = geo_lookup(ip_real)

    origen = data.get("origen")
    baliza_id = data.get("baliza_id") or "N/A"  # <- capturamos el UUID real

    fingerprint = data.get("fingerprint")

    if not origen or not fingerprint:
        return {"status": "error", "msg": "missing origen or fingerprint"}, 400

    from utils.fingerprint import guardar_fingerprint
    from utils.eventos import guardar_evento
    from utils.balizas import guardar_evento_baliza

    # -------------------------------------------------------------
    # 1. Guardar / reutilizar fingerprint
    # -------------------------------------------------------------
    source = {
        "type": "baliza_html",
        "origen": origen
    }

    fingerprint_id, _ = guardar_fingerprint(
        payload=fingerprint,
        source=source
    )
    eventos = cargar_eventos()

    # -------------------------------------------------------------
    # 2. Crear evento de visita
    # -------------------------------------------------------------
    evento = {
        "id_num": siguiente_id(eventos),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": request.remote_addr,
        "tipo": tipo_val,
        "evento": evento_val,
        "origen": baliza_id,
        "payload": origen_val, # payload,  # opcional, puedes poner json.dumps(fingerprint) si quieres
        "user_agent": request.user_agent.string,
        "so": so,
        "navegador": nav,
        "country": geo.get("country",""),
        "country_code": geo.get("country_code", ""),
        "region": geo.get("region", ""),
        "city": geo.get("city", ""),
        "lat": geo.get("lat", ""),
        "lon": geo.get("lon", ""),
        "isp": geo.get("isp", ""),
        "ip_local": ip_local,
        "hostname_local": hostname_local,
        "fingerprint_id": fingerprint_id
    }

    guardar_evento(evento)         # eventos.csv
    guardar_evento_baliza(evento)  # balizas_eventos.csv

    print(f"[BALIZA] Evento VIEW registrado para {origen} con fingerprint {fingerprint_id}")

    return {
        "status": "ok",
        "fingerprint_id": fingerprint_id
    }


@fingerprint_bp.route("/webhook/fingerprint", methods=["POST"])
def webhook_fingerprint():
    print("[DEBUG] /webhook/fingerprint llamada")
    data = request.get_json(force=True)
    origen = "HTML" # data.get("origen")
    fingerprint_data = data.get("fingerprint", {})

    from utils.fingerprint import guardar_fingerprint
    source = {
        "ip": request.remote_addr,
        "user_agent": request.user_agent.string
    }

    fp_id, es_nuevo = guardar_fingerprint(fingerprint_data, source)
    print(f"[FP] Fingerprint recibido desde {origen}: {fp_id} (nuevo: {es_nuevo})")

    # ← QUITAR cualquier código que cree eventos aquí
    # Solo guardar fingerprint

    return jsonify({"status": "ok", "fp_id": fp_id, "nuevo": es_nuevo})
