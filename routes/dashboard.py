from flask import Blueprint, render_template, request, redirect, url_for
from math import ceil

from utils.auth import requiere_login
from utils.eventos import cargar_eventos

dashboard_bp = Blueprint("dashboard", __name__)

# ---------------------------
# DASHBOARD
# ---------------------------
@dashboard_bp.route("/")
def dashboard():
    if not requiere_login():
        return redirect(url_for("auth.login"))

    eventos = cargar_eventos()
    eventos_ordenados = sorted(eventos, key=lambda x: x["timestamp"], reverse=True)

    # Paginación
    PAG_SIZE = 25
    pagina = int(request.args.get("page", 1))
    total_paginas = max(1, ceil(len(eventos_ordenados)/PAG_SIZE))
    inicio = (pagina-1)*PAG_SIZE
    fin = inicio + PAG_SIZE
    dashboard_rows = eventos_ordenados[inicio:fin]

    paginas = list(range(1, total_paginas+1))
    base_url = "/?"

    # Conteo por tipo de evento (ASCII)
    counts = {}
    for e in eventos:
        tipo = e.get("evento", "unknown")
        counts[tipo] = counts.get(tipo, 0) + 1

    labels = sorted(counts.keys())
    values = [counts[k] for k in labels]

    maxw = 60
    maxv = max(values) if values else 1
    lines = []
    for k in labels:
        l = int((counts[k]/maxv)*maxw)
        bar = "●"*l
        lines.append(f"{k[:20].ljust(20)} | {bar} {counts[k]}")
    ascii_chart = "\n".join(lines)

    return render_template(
        "dashboard.html",
        dashboard_rows=dashboard_rows,
        ascii_chart=ascii_chart,
        paginas=paginas,
        pagina=pagina,
        base_url=base_url,
        current_page="dashboard"
    )

# ---------------------------
# ADMIN
# ---------------------------
@dashboard_bp.route("/admin")
def admin():
    if not requiere_login():
        return redirect(url_for("auth.login"))

    eventos = cargar_eventos()

    f_ip = request.args.get("ip", "all")
    f_evento = request.args.get("evento", "all")
    f_origen = request.args.get("origen", "all")

    filtrados = [e for e in eventos
                 if (f_ip=="all" or e["ip"]==f_ip) and
                    (f_evento=="all" or e["evento"]==f_evento) and
                    (f_origen=="all" or e["origen"]==f_origen)]

    filtrados = sorted(filtrados, key=lambda x: x["timestamp"], reverse=True)

    PAG_SIZE = 25
    pagina = int(request.args.get("page", 1))
    total_paginas = max(1, ceil(len(filtrados)/PAG_SIZE))
    inicio = (pagina-1)*PAG_SIZE
    fin = inicio+PAG_SIZE
    eventos_pagina = filtrados[inicio:fin]

    ips = sorted({e["ip"] for e in eventos})
    eventos_unicos = sorted({e["evento"] for e in eventos})
    origenes = sorted({e["origen"] for e in eventos})
    base_url = f"/admin?ip={f_ip}&evento={f_evento}&origen={f_origen}"

    return render_template(
        "admin.html",
        current_page="admin",
        eventos_pagina=eventos_pagina,
        pagina=pagina,
        paginas=list(range(1,total_paginas+1)),
        ips=ips,
        eventos=eventos_unicos,
        origenes=origenes,
        f_ip=f_ip,
        f_evento=f_evento,
        f_origen=f_origen,
        base_url=base_url
    )

# ---------------------------
# DELETE EVENT INDIVIDUAL
# ---------------------------
@dashboard_bp.post("/admin/delete/<int:id_num>")
def delete_event(id_num):
    if not requiere_login():
        return redirect(url_for("auth.login"))
    eventos = cargar_eventos()
    eventos = [e for e in eventos if e["id_num"] != id_num]
    guardar_eventos(eventos)
    return redirect(request.referrer or "/admin")

# ---------------------------
# DELETE ALL
# ---------------------------
@dashboard_bp.route("/admin/delete_all")
def delete_all():
    if not requiere_login():
        return redirect(url_for("auth.login"))
    guardar_eventos([])
    return redirect("/admin")
