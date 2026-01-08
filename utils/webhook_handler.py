# utils/webhook_handler.py

"""
Módulo para procesar eventos recibidos por webhook.

Función principal:
- procesar_webhook: captura datos de request (GET o POST),
  construye un evento normalizado, obtiene información de IP
  y geolocalización, registra el evento y guarda en CSV.
"""

import json
from datetime import datetime
from flask import request, jsonify

from utils.eventos import cargar_eventos, guardar_evento, siguiente_id
from utils.balizas import existe_baliza, guardar_evento_baliza
from utils.utils import obtener_ip_hostname, obtener_ip_real, parse_user_agent
from utils.geoip import geo_lookup

# from utils.fingerprint import ejecutar_fingerprint_baliza



def procesar_webhook():
    """
    Procesa un request entrante como webhook.

    Flujo:
    1. Captura datos del request (POST JSON o form, GET args)
    2. Construye un payload completo en JSON
    3. Determina evento, origen y tipo automáticamente
    4. Obtiene IP real, hostname local y geolocalización
    5. Extrae SO y navegador desde user_agent
    6. Crea el evento y lo guarda en eventos generales
    7. Si el origen corresponde a una baliza, lo guarda también en baliza

    Returns:
        flask.jsonify: {"status": "ok", "id_num": <id del evento>}
    """
    print("[DEBUG] procesar_webhook FUNCTION <-- llamada")  # <-- print inicial

    # 1. Cargar eventos existentes
    eventos = cargar_eventos()

    # 2. Capturar datos del request
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form.to_dict()
    else:
        data = request.args.to_dict()

    print(f"[DEBUG] Datos capturados en webhook_handler: {data}")  # <-- print aquí

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

    # 8. Construir evento normalizado
    nuevo_evento = {
        "id_num": siguiente_id(eventos),
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
        "ip": ip_real,
        "tipo": tipo_val,
        "evento": evento_val,
        "origen": origen_val,
        "payload": payload,
        "so": so,
        "navegador": nav,
        "user_agent": ua_str,
        "country": geo.get("country",""),
        "country_code": geo.get("country_code",""),
        "region": geo.get("region",""),
        "city": geo.get("city",""),
        "lat": geo.get("lat",""),
        "lon": geo.get("lon",""),
        "isp": geo.get("isp",""),
        "ip_local": ip_local,
        "hostname_local": hostname_local,
        "fingerprint_id": ""

    }

    # 9. Guardar evento en CSV general
    # eventos.append(nuevo_evento)
    # guardar_eventos(eventos)

    # 10. Guardar evento en baliza si aplica
    # if existe_baliza(origen_val):
    #     guardar_evento_baliza(nuevo_evento)
    #     # Solo loguear la visita; el fingerprint se ejecuta desde JS
    #     print(f"[INFO] Baliza visitada: {origen_val} desde IP {ip_real}")

    print("[DEBUG] procesar_webhook FUNCTION <-- salida")  # <-- print inicial

    return jsonify({"status": "ok", "id_num": nuevo_evento["id_num"]})
