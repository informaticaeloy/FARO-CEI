# routes/balizas.py
from flask import Blueprint, jsonify
from flask import render_template, request, redirect, url_for, abort, send_file, send_from_directory
from datetime import datetime
import os, csv, uuid, shutil

from utils.balizas import *
from utils.tipos_y_eventos import *
from utils.servidores import *

from utils.eventos import *
from utils.auth import requiere_login
from utils.balizas import cargar_baliza, guardar_evento_baliza
from . import BALIZAS_EVENTOS_CSV
from utils.utils import obtener_ip_real, obtener_ip_hostname, parse_user_agent
from utils.geoip import geo_lookup
from utils.tor_y_vpn import analyze_ip

#from utils.eventos import guardar_evento, cargar_eventos, siguiente_id
#from utils.balizas import guardar_evento_baliza
#from utils.utils import obtener_ip_real, obtener_ip_hostname, parse_user_agent
#from utils.geoip import geo_lookup
balizas_bp = Blueprint("balizas", __name__)

############################################################################################ inico copiado a BP
# ------------------------------------------------------------------------ INICIO BALIZAS
# ---------- RUTA: listado / creación form (GET) ----------
@balizas_bp.route("/balizas")
def balizas():
    if not requiere_login():
        return redirect(url_for("login"))

    tipos = cargar_tipos_de_tipos()  # lista de dicts {"nombre": "...", "color": "..."}
    eventos = cargar_tipos_de_eventos()

    # Crear diccionarios para lookup rápido
    tipos_dict = {t["nombre"]: t["color"] for t in tipos}
    eventos_dict = {e["nombre"]: e["color"] for e in eventos}

    balizas_list = load_balizas()
    balizas_list.sort(key=lambda b: b['timestamp'], reverse=True)

    # --- NUEVO: conteo de visitas ---
    visitas_por_origen = contar_visitas_por_baliza()

    for b in balizas_list:
        origen = b.get("origen")
        visitas = visitas_por_origen.get(origen, 0)

        b["visitas"] = visitas
        b["visitada"] = visitas > 0

    return render_template("balizas.html",
                           balizas=balizas_list,
                           tipos_dict=tipos_dict,
                           eventos_dict=eventos_dict,
                           current_page="balizas")


@balizas_bp.route("/balizas/nueva", methods=["GET", "POST"])
def baliza_nueva():
    if not requiere_login():
        return redirect(url_for("login"))

    # --- GET: mostrar formulario ---
    if request.method == "GET":
        tipos = cargar_tipos_de_tipos()
        eventos = cargar_tipos_de_eventos()
        servidores = cargar_servidores()
        return render_template(
            "balizas_nueva.html",
            tipos=tipos,
            eventos=eventos,
            servidores=servidores
        )

    # --- POST: procesar envío ---
    comentario = request.form.get("comentario", "")
    tipo = request.form.get("tipo", "TIPO1")
    evento = request.form.get("evento", "EVENTO1")
    origen = request.form.get("origen") or str(uuid.uuid4())
    servidor_nombre = request.form.get("servidor", "")

    # localizar servidor seleccionado
    servidores = cargar_servidores()
    servidor_obj = next((s for s in servidores if s.get("nombre") == servidor_nombre), None)

    servidor_url = servidor_obj.get("ruta", "") if servidor_obj else ""

    # Obtener ID numérico incremental
    balizas = load_balizas()
    if balizas:
        max_id = max(int(b['id']) for b in balizas)
        baliza_id = str(max_id + 1)
    else:
        baliza_id = "1"

    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    row = {
        "id": baliza_id,
        "timestamp": ts,
        "comentario": comentario,
        "tipo": tipo,
        "evento": evento,
        "origen": origen,
        "servidor": servidor_nombre,
        "servidor_url": servidor_obj["ruta"] if servidor_obj else ""   #    "servidor_url": servidor_url
    }

    save_baliza(row)

    try:
        # target_png = os.path.join(BALIZAS_FOLDER, f"{baliza_id}.png")
        target_png = os.path.join(BALIZAS_FOLDER, f"{origen}.png")
        if os.path.exists(ORIGIN_PNG):
            shutil.copyfile(ORIGIN_PNG, target_png)
    except Exception as e:
        app.logger.warning(f"No se pudo copiar origin.png para baliza {baliza_id}: {e}")

    return redirect(url_for("balizas.balizas"))


@balizas_bp.route("/balizas/<baliza_id>/editar", methods=["GET","POST"])
def balizas_editar(baliza_id):
    if not requiere_login():
        return redirect(url_for("login"))

    balizas_list = load_balizas()
    servidores_list = cargar_servidores()   # lista de dicts

    bal = next((b for b in balizas_list if b.get("id") == baliza_id), None)
    if not bal:
        abort(404)

    if request.method == "POST":
        bal["comentario"] = request.form.get("comentario", bal.get("comentario", ""))
        bal["tipo"] = request.form.get("tipo", bal.get("tipo", ""))
        bal["evento"] = request.form.get("evento", bal.get("evento", ""))
        bal["origen"] = request.form.get("origen", bal.get("origen", ""))

        # --- RESOLUCIÓN DEL SERVIDOR ---
        servidor_nombre = request.form.get("servidor", "").strip()
        bal["servidor"] = servidor_nombre

        # CORRECCIÓN: usar dicts, no objetos
        servidor_obj = next((s for s in servidores_list if s["nombre"] == servidor_nombre), None)
        bal["servidor_url"] = servidor_obj["ruta"] if servidor_obj else ""

        update_balizas_csv(balizas_list)
        return redirect(url_for("balizas.balizas"))

    tipos = cargar_tipos_de_tipos()
    eventos = cargar_tipos_de_eventos()
    servidores = cargar_servidores()

    return render_template(
        "baliza_editar.html",
        baliza=bal,
        tipos=tipos,
        eventos=eventos,
        servidores=servidores,
        current_page="balizas")


# ---------- RUTA: eliminar baliza (POST) ----------
@balizas_bp.route("/balizas/<baliza_id>/eliminar", methods=["POST"])
def baliza_eliminar(baliza_id):
    if not requiere_login():
        return redirect(url_for("auth.login"))

    balizas_list = load_balizas()
    balizas_list = [b for b in balizas_list if b.get("id") != baliza_id]
    update_balizas_csv(balizas_list)

    # borrar png asociado
    png_path = os.path.join(BALIZAS_FOLDER, f"{baliza_id}.png")
    try:
        if os.path.exists(png_path):
            os.remove(png_path)
    except Exception as e:
        app.logger.warning(f"No se pudo borrar {png_path}: {e}")

    return redirect(url_for("balizas.balizas"))


# ---------- RUTA: estadísticas (GET) ----------
@balizas_bp.route("/balizas/<baliza_id>/stats")
def baliza_stats(baliza_id):
    if not requiere_login():
        return redirect(url_for("login"))

    # Cargar todas las balizas
    balizas = load_balizas()

    # Buscar la baliza por id (id numérico correlativo)
    baliza = next((b for b in balizas if str(b.get("id")) == str(baliza_id)), None)
    if not baliza:
        return "Baliza no encontrada", 404

    # Crear diccionarios para lookup rápido
    tipos = cargar_tipos_de_tipos()
    eventos = cargar_tipos_de_eventos()
    tipos_dict = {t["nombre"]: t["color"] for t in tipos}
    eventos_dict = {e["nombre"]: e["color"] for e in eventos}

    balizas_list = load_balizas()
    balizas_list.sort(key=lambda b: b['timestamp'], reverse=True)

    # UUID completo y limpio de la baliza
    uuid_real = str(baliza.get("origen", "")).strip().replace('"', '')

    visitas = []

    # Leer eventos de balizas y hacer matching por 'origen'
    if os.path.exists(BALIZAS_EVENTOS_CSV):
        with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                evento_uuid = str(r.get("origen", "")).strip().replace('"', '')
                if evento_uuid == uuid_real:
                    # opcional: limpiar campos para la plantilla
                    r["timestamp"] = r.get("timestamp", "")
                    r["ip"] = r.get("ip", "")
                    r["country"] = r.get("country", "") or r.get("country_code", "") or "Desconocido"
                    r["so"] = r.get("so", "")
                    r["navegador"] = r.get("navegador", "")
                    visitas.append(r)

    # Ordenar visitas por timestamp descendente (siempre que el timestamp sea comparable como string ISO)
    try:
        visitas.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    except Exception:
        pass

    # Para depuración temporal, puedes descomentar:
    # app.logger.debug("UUID buscado: %s — visitas encontradas: %d", uuid_real, len(visitas))
    # if visitas: app.logger.debug("Primera visita: %s", visitas[0])

    # Pasamos la lista como 'visitas' porque la plantilla usa ese nombre
    return render_template(
        "baliza_stats.html",
        visitas=visitas,
        baliza=baliza,
        current_page="balizas",
        tipos_dict=tipos_dict,
        eventos_dict=eventos_dict
    )


# ---------- RUTA: servir PNG y registrar visita ----------
@balizas_bp.route("/balizas/png/<baliza_id>.png")
def baliza_image(baliza_id):
    png_path = os.path.join(BALIZAS_FOLDER, f"{baliza_id}.png")
    if not os.path.exists(png_path):
        abort(404)

    # registrar evento
    ensure_balizas_eventos_header()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")

    with open(BALIZAS_EVENTOS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().replace(microsecond=0).isoformat() + "Z", baliza_id, ip, ua])

    return send_file(png_path, mimetype="image/png")


# --------- Ruta en Flask para servir archivos de baliza
@balizas_bp.route("/balizas/files/<filename>")
def baliza_files(filename):
    return send_from_directory(BALIZAS_FOLDER, filename, as_attachment=True)


# ---------- RUTA: vista HTML de baliza (fingerprint) ----------
@balizas_bp.route("/balizas/view/<origen>")
def baliza_view(origen):
    if not existe_baliza(origen):
        abort(404)

    # Origen lógico de la visita (HTML por defecto)
    origen_visita = request.args.get("o", "HTML").upper()

    # Registrar visita (ya maneja evento, IP, TOR/VPN, fingerprint si hay)
    registrar_visita_baliza(request, id_baliza=origen, origen=origen_visita)

    return render_template(
        "baliza_view.html",
        origen=origen,
        origen_visita=origen_visita
    )

################################################################################### copiado a BP

# --------------------------------------------------------- Endpoint para registrar evento
@balizas_bp.route("/balizas/event", methods=["POST"])
def balizas_event():
    # print(">>> Entro en /balizas/event")
    data = request.get_json(force=True)

    evento = {
        "id_num": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "tipo": data.get("tipo", "HTML"),
        "evento": data.get("evento", "VIEW"),
        "origen": data.get("origen"),
        "fingerprint_id": data.get("fingerprint_id"),
        "payload": None,
        "so": None,
        "navegador": None,
        "user_agent": request.headers.get("User-Agent"),
        "country": None,
        "country_code": None,
        "region": None,
        "city": None,
        "lat": None,
        "lon": None,
        "isp": None,
        "ip_local": None,
        "hostname_local": None
    }

    # guardar_evento_baliza(evento)

    return {"status": "disabled"}


@balizas_bp.route("/balizas/<baliza_id>.png")
def baliza_png(baliza_id):

    if not existe_baliza(baliza_id):
        abort(404)


    # IP y entorno
    ip_real = obtener_ip_real(request) or request.remote_addr
    geo = geo_lookup(ip_real)

    host = obtener_ip_hostname()
    ua_str = request.user_agent.string or ""
    so, nav = parse_user_agent(ua_str)

    # 3. Evento y origen
    # Recuperar datos de la baliza
    baliza = cargar_baliza(baliza_id)  # Debe devolver algo como {"evento": "VIEW", "tipo": "INFO", ...}
    print(baliza)
    evento_val = baliza.get("evento", "VIEW")
    tipo_val = baliza.get("tipo", "INFO")

    origen_val = "PNG"

    # 4. Tipo derivado automáticamente
    ev_upper = evento_val.upper()
    # tipo_val = ("ERROR" if ev_upper in ("ERROR","FALLO","ALERTA")
    #             else "WARN" if ev_upper in ("WARN","AVISO")
    #             else "INFO" if ev_upper in ("INFO","CHECK","OK")
    #             else "EVENT")

    ip_intel = analyze_ip(ip_real.strip())

    eventos = cargar_eventos()

    evento = {
        "id_num": siguiente_id(eventos),
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "ip": ip_real.strip(),
        "tipo": tipo_val,
        "evento": evento_val,
        "origen": baliza_id,
        "payload": origen_val,  # PNG
        "so": so,
        "navegador": nav,
        "user_agent": ua_str,
        "country": geo.get("country", "") or "",
        "country_code": geo.get("country_code", "") or "",
        "region": geo.get("region", "") or "",
        "city": geo.get("city", "") or "",
        "lat": geo.get("lat", "") or "",
        "lon": geo.get("lon", "") or "",
        "isp": (geo.get("isp") or "").strip().upper(),
        "ip_local": host.get("ip_local", ""),
        "hostname_local": host.get("hostname_local", ""),
        "fingerprint_id": request.cookies.get("fingerprint_id", "").strip(),
        "flag_tor": bool(ip_intel.get("TOR", False)),
        "flag_vpn": bool(ip_intel.get("VPN", False))

        # "flag_tor": analyze_ip(ip_real.strip())["TOR"],
        # "flag_vpn": analyze_ip(ip_real.strip())["VPN"]
    }

    guardar_evento(evento)
    guardar_evento_baliza(evento)

    # Servir el PNG real
    return send_from_directory(
        directory="balizas",
        path=f"{baliza_id}.png",
        mimetype="image/png"
    )
