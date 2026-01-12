# routes/logins.py
from flask import Blueprint, render_template, request, redirect, url_for
from math import ceil

from utils.auth import requiere_login
from utils.logins import cargar_login_attempts
from utils.geoip import geo_lookup  # si lo usas para mostrar país/ciudad

logins_bp = Blueprint("logins", __name__)

@logins_bp.route("/logins")
def dashboard_logins():
    if not requiere_login():
        return redirect(url_for("auth.login"))

    intentos = cargar_login_attempts()

    # filtros
    f_ip = request.args.get("ip", "all")
    f_user = request.args.get("usuario", "all")
    f_resultado = request.args.get("resultado", "all")

    filtrados = []
    for e in intentos:
        if f_ip != "all" and e["ip"] != f_ip:
            continue
        if f_user != "all" and e["usuario"] != f_user:
            continue
        if f_resultado != "all" and e["resultado"] != f_resultado:
            continue
        filtrados.append(e)

    # ordenar por timestamp desc
    filtrados = sorted(filtrados, key=lambda x: x["timestamp"], reverse=True)

    # paginación
    PAG_SIZE = 25
    pagina = int(request.args.get("page", 1))
    total_paginas = max(1, ceil(len(filtrados)/PAG_SIZE))
    inicio = (pagina - 1) * PAG_SIZE
    fin = inicio + PAG_SIZE
    intentos_pagina = filtrados[inicio:fin]

    # valores únicos filtros
    ips = sorted({e["ip"] for e in intentos})
    usuarios = sorted({e["usuario"] for e in intentos})
    resultados = ["success", "failed", "locked"]

    base_url = "/logins?"

    return render_template(
        "dashboard_logins.html",
        current_page="logins",
        logins=intentos_pagina,
        geo_lookup=geo_lookup,
        pagina=pagina,
        paginas=list(range(1, total_paginas + 1)),
        ips=ips,
        usuarios=usuarios,
        resultados=resultados,
        f_ip=f_ip,
        f_user=f_user,
        f_resultado=f_resultado,
        base_url=base_url
    )

#
#
#
# # ---------------------------
# # DASHBOARD LOGINS
# # ---------------------------
#
# @app.route("/logins")
# def dashboard_logins():
#     if not requiere_login():
#         return redirect(url_for("auth.login"))
#
#     intentos = cargar_login_attempts()
#
#     # filtros
#     f_ip = request.args.get("ip", "all")
#     f_user = request.args.get("usuario", "all")
#     f_resultado = request.args.get("resultado", "all")
#
#     filtrados = []
#     for e in intentos:
#         if f_ip != "all" and e["ip"] != f_ip:
#             continue
#         if f_user != "all" and e["usuario"] != f_user:
#             continue
#         if f_resultado != "all" and e["resultado"] != f_resultado:
#             continue
#         filtrados.append(e)
#
#     # ordenar por timestamp desc
#     filtrados = sorted(filtrados, key=lambda x: x["timestamp"], reverse=True)
#
#     # paginación
#     PAG_SIZE = 25
#     pagina = int(request.args.get("page", 1))
#     total_paginas = max(1, ceil(len(filtrados)/PAG_SIZE))
#     inicio = (pagina - 1) * PAG_SIZE
#     fin = inicio + PAG_SIZE
#     intentos_pagina = filtrados[inicio:fin]
#
#     # valores únicos filtros
#     ips = sorted({e["ip"] for e in intentos})
#     usuarios = sorted({e["usuario"] for e in intentos})
#     resultados = ["success", "failed", "locked"]  # estándar
#
#     #base_url = f"/?ip={f_ip}&usuario={f_user}&resultado={f_resultado}"
#     base_url = "/logins?"  # No hay filtros en dashboard, así que es simple
#     return render_template(
#         "dashboard_logins.html",
#         current_page="logins",
#         logins=intentos_pagina,
#         geo_lookup=geo_lookup,
#         pagina=pagina,
#         paginas=list(range(1, total_paginas + 1)),
#         ips=ips,
#         usuarios=usuarios,
#         resultados=resultados,
#         f_ip=f_ip,
#         f_user=f_user,
#         f_resultado=f_resultado,
#         base_url=base_url
#     )
