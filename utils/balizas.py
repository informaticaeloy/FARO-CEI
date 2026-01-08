# utils/balizas.py
import csv
import os
import shutil

from datetime import datetime
from utils.eventos import guardar_evento, cargar_eventos, siguiente_id
from utils.geoip import geo_lookup
from utils.utils import obtener_ip_real, obtener_ip_hostname
from utils.utils import parse_user_agent

from . import BASE_DIR, DATA_DIR, BALIZAS_FOLDER, BALIZAS_CSV, BALIZAS_EVENTOS_CSV, ORIGIN_PNG

# Asegurar carpetas
os.makedirs(BALIZAS_FOLDER, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

BALIZAS_KEYS = ["id", "timestamp", "comentario", "tipo", "evento", "origen", "servidor", "servidor_url"]

# ------------------- BALIZAS -------------------

def ensure_balizas_header():
    """Crea la cabecera de CSV de balizas si no existe o está vacía."""
    if not os.path.exists(BALIZAS_CSV) or os.path.getsize(BALIZAS_CSV) == 0:
        with open(BALIZAS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "timestamp", "comentario", "tipo", "evento", "origen", "servidor", "servidor_url"])


def load_balizas():
    """Carga todas las balizas, ordenadas por id numérico ascendente."""
    balizas = []
    if not os.path.exists(BALIZAS_CSV):
        return balizas

    with open(BALIZAS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        balizas = list(reader)

    # Ordenar por ID numérico
    balizas.sort(key=lambda x: int(x["id"]))
    return balizas


def save_baliza(row: dict):
    """Añade una nueva baliza y genera los archivos PNG y HTML asociados."""
    ensure_balizas_header()
    with open(BALIZAS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            row["id"],
            row["timestamp"],
            row.get("comentario", ""),
            row.get("tipo", ""),
            row.get("evento", ""),
            row.get("origen", ""),
            row.get("servidor", ""),
            row.get("servidor_url", "")
        ])
    generar_png_baliza(row["origen"])
    html_path = os.path.join(BALIZAS_FOLDER, f"{row['origen']}.html")
    generar_html_baliza(row["origen"], html_path)


def update_balizas_csv(balizas_list):
    """Sobrescribe todas las balizas en el CSV (update/delete)."""
    with open(BALIZAS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "timestamp", "comentario", "tipo", "evento", "origen", "servidor", "servidor_url"])
        for b in balizas_list:
            writer.writerow([
                b.get("id", ""),
                b.get("timestamp", ""),
                b.get("comentario", ""),
                b.get("tipo", ""),
                b.get("evento", ""),
                b.get("origen", ""),
                b.get("servidor", ""),
                b.get("servidor_url", "")
            ])


def existe_baliza(origen: str) -> bool:
    """Devuelve True si existe una baliza con ese origen."""
    return any(b["origen"] == origen for b in load_balizas())


# ------------------- EVENTOS DE BALIZAS -------------------

def ensure_balizas_eventos_header():
    """Crea la cabecera de CSV de eventos si no existe."""
    if not os.path.exists(BALIZAS_EVENTOS_CSV) or os.path.getsize(BALIZAS_EVENTOS_CSV) == 0:
        with open(BALIZAS_EVENTOS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id_num", "timestamp", "ip", "tipo", "evento", "origen",
                "payload", "so", "navegador", "user_agent",
                "country", "country_code", "region", "city", "lat", "lon", "isp",
                "ip_local", "hostname_local", "fingerprint_id", "flag_tor", "flag_vpn"
            ])


def guardar_evento_baliza(evento: dict):
    # print(f"[DEBUG] ENTRO EN UTILS/BALIZAS.PY -> guardar_evento_baliza(evento: dict)")
    """Añade un evento de baliza al CSV."""
    ensure_balizas_eventos_header()
    with open(BALIZAS_EVENTOS_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id_num", "timestamp", "ip", "tipo", "evento", "origen",
            "payload", "so", "navegador", "user_agent",
            "country", "country_code", "region", "city", "lat", "lon", "isp",
            "ip_local", "hostname_local", "fingerprint_id", "flag_tor", "flag_vpn"

        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(evento)

# "fingerprint_id",
def contar_visitas_por_baliza() -> dict:
    """Devuelve el número de visitas por baliza (clave: origen)."""
    visitas = {}
    if not os.path.exists(BALIZAS_EVENTOS_CSV):
        return visitas

    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            origen = row.get("origen")
            if origen:
                visitas[origen] = visitas.get(origen, 0) + 1
    return visitas


def registrar_fingerprint_en_evento_baliza(origen: str, fingerprint_id: str) -> bool:
    """Añade el fingerprint_id al último evento de baliza sin valor asignado."""
    if not os.path.exists(BALIZAS_EVENTOS_CSV):
        return False

    filas = []
    ultima_fila_objetivo = None

    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            filas.append(row)
            if row.get("origen") == origen and not row.get("fingerprint_id"):
                ultima_fila_objetivo = row

    if not ultima_fila_objetivo:
        return False

    ultima_fila_objetivo["fingerprint_id"] = fingerprint_id

    with open(BALIZAS_EVENTOS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filas)

    return True


# ------------------- GENERACIÓN DE ARCHIVOS -------------------

def generar_html_baliza(origen: str, target_path: str):
    """Genera un HTML tipo formulario con la baliza integrada."""
    plantilla = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Baliza {origen}</title></head>
<body>
<script src="/static/fingerprint/orchestrator.js"></script>
<script type="module">
(async () => {{
    const fpData = await window.runFingerprint();
    await fetch("/webhook/fingerprint", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ origen: "{origen}", fingerprint: fpData, tipo: "HTML", evento: "VIEW" }})
    }});
}})();
</script>
</body>
</html>
"""
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(plantilla)


def generar_png_baliza(origen: str) -> str:
    """Copia origin.png a la baliza correspondiente."""
    target_png = os.path.join(BALIZAS_FOLDER, f"{origen}.png")
    if os.path.exists(ORIGIN_PNG):
        shutil.copyfile(ORIGIN_PNG, target_png)
    return target_png


def enriquecer_evento_baliza(origen, fingerprint_id, fp_components, metadata):
    """
    Enriquecimiento del último evento VIEW de una baliza
    usando datos de fingerprint
    """
    eventos = cargar_eventos_baliza(origen)
    if not eventos:
        return False

    # buscar último VIEW sin fingerprint
    for evento in reversed(eventos):
        if evento.get("evento") == "VIEW" and not evento.get("fingerprint_id"):
            evento["fingerprint_id"] = fingerprint_id

            evento["so"] = fp_components.get("os")
            evento["navegador"] = fp_components.get("browserName")

            evento["hostname_local"] = metadata.get("hostname")
            evento["ip_local"] = metadata.get("localIp")

            evento["enriched"] = True
            guardar_eventos_baliza(origen, eventos)
            return True

    return False


def registrar_visita_baliza(request, id_baliza: str, origen: str):
    """
    Registra una visita a una baliza (HTML, PNG, etc.)
    Incluye flags TOR/VPN calculados automáticamente.
    """

    from utils.tor_y_vpn import analyze_ip  # import aquí para evitar loops

    eventos = cargar_eventos()

    # IP real y geolocalización
    ip_real = obtener_ip_real(request) or "N/A"
    geo = geo_lookup(ip_real)

    # Host local
    host_info = obtener_ip_hostname()

    # User-Agent
    ua_str = request.user_agent.string or ""
    so, nav = parse_user_agent(ua_str)

    # Calcular flags TOR/VPN
    tor_vpn_flags = analyze_ip(ip_real.strip())
    flag_tor = tor_vpn_flags.get("TOR", False)
    flag_vpn = tor_vpn_flags.get("VPN", False)

    evento = {
        "id_num": siguiente_id(eventos),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": ip_real,
        "tipo": "HTML",
        "evento": "VIEW",
        "origen": origen,
        "payload": "",  # Aquí se puede poner "PNG" si es PNG
        "user_agent": ua_str,
        "so": so,
        "navegador": nav,
        "country": geo.get("country", ""),
        "country_code": geo.get("country_code", ""),
        "region": geo.get("region", ""),
        "city": geo.get("city", ""),
        "lat": geo.get("lat", ""),
        "lon": geo.get("lon", ""),
        "isp": (geo.get("isp") or "").strip().upper(),
        "ip_local": host_info.get("ip_local", ""),
        "hostname_local": host_info.get("hostname_local", ""),
        "fingerprint_id": "",
        "flag_tor": flag_tor,
        "flag_vpn": flag_vpn
    }

    # Guardar en eventos.csv
    guardar_evento(evento)

    # Guardar en eventos_baliza.csv
    guardar_evento_baliza(evento)


def cargar_baliza(baliza_id: str) -> dict:
    """
    Carga la baliza por su ID desde el CSV.
    Devuelve un diccionario con al menos 'evento' y 'tipo'.
    """
    print("BALIZA")
    print(baliza_id)
    if not os.path.exists(BALIZAS_CSV):
        return {}
    try:
        with open(BALIZAS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=BALIZAS_KEYS)
            next(reader)  # saltar cabecera
            for row in reader:
                if row["origen"] == baliza_id:
                    return {
                        "tipo": row.get("tipo", "INFO"),
                        "evento": row.get("evento", "VIEW")
                    }
    except Exception:
        return {}
    return {}