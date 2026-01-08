# routes/configuracion.py
from flask import Blueprint, request, redirect, url_for, render_template
from utils.auth import requiere_login
from utils.tipos_y_eventos import (
    cargar_tipos_de_tipos, cargar_tipos_de_eventos,
    crear_tipo, editar_tipo, eliminar_tipo,
    crear_evento, editar_evento, eliminar_evento
)
from utils.servidores import cargar_servidores, guardar_servidores
from utils.fingerprint_policy import load_fingerprint_policy, save_fingerprint_policy

import csv

configuracion_bp = Blueprint("configuracion", __name__)

# ---------- PÁGINA DE CONFIGURACIÓN ----------
@configuracion_bp.route("/configuracion", methods=["GET", "POST"])
def config_page():
    if not requiere_login():
        return redirect(url_for("auth.login"))

    tipos_de_tipos = cargar_tipos_de_tipos()
    tipos_de_eventos = cargar_tipos_de_eventos()
    servidores = cargar_servidores()
    fingerprint_policy = load_fingerprint_policy()

    return render_template(
        "configuracion.html",
        current_page="configuracion",
        tipos_de_tipos=tipos_de_tipos,
        tipos_de_eventos=tipos_de_eventos,
        servidores=servidores,
        fingerprint_policy=fingerprint_policy

    )

# ---------- TIPOS ----------
@configuracion_bp.route("/add_tipo", methods=["POST"])
def route_add_tipo():
    crear_tipo(request.form)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/edit_tipo", methods=["POST"])
def route_edit_tipo():
    editar_tipo(request.form)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/delete_tipo", methods=["POST"])
def route_delete_tipo():
    eliminar_tipo(request.form)
    return redirect(url_for("configuracion.config_page"))

# ---------- EVENTOS ----------
@configuracion_bp.route("/add_evento", methods=["POST"])
def route_add_evento():
    crear_evento(request.form)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/edit_evento", methods=["POST"])
def route_edit_evento():
    editar_evento(request.form)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/delete_evento", methods=["POST"])
def route_delete_evento():
    eliminar_evento(request.form)
    return redirect(url_for("configuracion.config_page"))

# ---------- CRUD SERVIDORES ----------
@configuracion_bp.route("/add_servidor", methods=["POST"])
def add_servidor():
    nombre = request.form.get("nombre", "").strip()
    ruta = request.form.get("ruta", "").strip()
    if nombre and ruta:
        servidores = cargar_servidores()
        servidores.append({"nombre": nombre, "ruta": ruta})
        guardar_servidores(servidores)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/edit_servidor", methods=["POST"])
def edit_servidor():
    original = request.form.get("original", "").strip()
    nombre = request.form.get("nombre", "").strip()
    ruta = request.form.get("ruta", "").strip()

    servidores = cargar_servidores()
    for s in servidores:
        if s["nombre"] == original:
            s["nombre"] = nombre
            s["ruta"] = ruta
            break
    guardar_servidores(servidores)
    return redirect(url_for("configuracion.config_page"))

@configuracion_bp.route("/delete_servidor", methods=["POST"])
def delete_servidor():
    nombre = request.form.get("nombre", "").strip()
    servidores = [s for s in cargar_servidores() if s["nombre"] != nombre]
    guardar_servidores(servidores)
    return redirect(url_for("configuracion.config_page"))




@configuracion_bp.route("/configuracion/fingerprint-policy", methods=["POST"])
def update_fingerprint_policy():
    if not requiere_login():
        return "", 401

    policy = load_fingerprint_policy()

    # --------- CHECKS ----------
    for key in policy.get("checks", {}).keys():
        form_key = f"check_{key}"
        if form_key in request.form:
            try:
                policy["checks"][key] = int(request.form[form_key])
            except ValueError:
                pass  # evita romper la config por input inválido

    # --------- THRESHOLDS -------
    try:
        policy["confidence_levels"]["HIGH"] = int(
            request.form.get(
                "confidence_high",
                policy["confidence_levels"]["HIGH"]
            )
        )
    except ValueError:
        pass

    try:
        policy["confidence_levels"]["MEDIUM"] = int(
            request.form.get(
                "confidence_medium",
                policy["confidence_levels"]["MEDIUM"]
            )
        )
    except ValueError:
        pass

    # LOW es implícito: score < MEDIUM

    # --------- PERSISTENCIA -----
    save_fingerprint_policy(policy)

    return redirect(url_for("configuracion.config_page"))



# # ------------------------------------------------------------------------------------
# # ---------------------------------------------------------------------- CONFIGURACION
# # ------------------------------------------------------------------------------------
# @app.route("/configuracion", methods=["GET", "POST"])
# def configuracion():
#     if not requiere_login():
#         return redirect(url_for("auth.login"))
#
#     tipos_de_tipos = cargar_tipos_de_tipos()
#     tipos_de_eventos = cargar_tipos_de_eventos()
#     servidores = cargar_servidores()
#
#     return render_template(
#         "configuracion.html",
#         current_page="configuracion",
#         tipos_de_tipos=tipos_de_tipos,
#         tipos_de_eventos=tipos_de_eventos,
#         servidores=servidores
#     )
#
#
# # ---------------- TIPOS ----------------
#
# @app.route("/add_tipo", methods=["POST"])
# def route_add_tipo():
#     crear_tipo(request.form)
#     return redirect(url_for("configuracion"))
#
# @app.route("/edit_tipo", methods=["POST"])
# def route_edit_tipo():
#     editar_tipo(request.form)
#     return redirect(url_for("configuracion"))
#
# @app.route("/delete_tipo", methods=["POST"])
# def route_delete_tipo():
#     eliminar_tipo(request.form)
#     return redirect(url_for("configuracion"))
#
#
# # ---------------- EVENTOS ----------------
#
# @app.route("/add_evento", methods=["POST"])
# def route_add_evento():
#     crear_evento(request.form)
#     return redirect(url_for("configuracion"))
#
# @app.route("/edit_evento", methods=["POST"])
# def route_edit_evento():
#     editar_evento(request.form)
#     return redirect(url_for("configuracion"))
#
# @app.route("/delete_evento", methods=["POST"])
# def route_delete_evento():
#     eliminar_evento(request.form)
#     return redirect(url_for("configuracion"))
#
# # ------------------------------------------------------------------------------------
# # ------------------------------------------------------------------ FIN CONFIGURACION
# # ------------------------------------------------------------------------------------
#
#
# # ===========================================================
# # CRUD TIPOS DE TIPOS
# # ===========================================================
#
#
# @app.route("/add_tipo", methods=["POST"])
# def add_tipo():
#     nombre = request.form.get("nombre", "").strip()
#     color = request.form.get("color", "").strip()
#
#     if nombre and color:
#         ruta = "data/tipos_de_tipos.csv"
#         with open(ruta, "a", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow([nombre, color])
#
#     return redirect(url_for("configuracion"))
#
#
# @app.route("/edit_tipo", methods=["POST"])
# def edit_tipo():
#     original = request.form.get("original", "").strip()
#     nombre = request.form.get("nombre", "").strip()
#     color = request.form.get("color", "").strip()
#
#     ruta = "data/tipos_de_tipos.csv"
#     rows = []
#
#     with open(ruta, "r", encoding="utf-8") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row and row[0] == original:
#                 rows.append([nombre, color])
#             else:
#                 rows.append(row)
#
#     with open(ruta, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)
#
#     return redirect(url_for("configuracion"))
#
#
# @app.route("/delete_tipo", methods=["POST"])
# def delete_tipo():
#     nombre = request.form.get("nombre", "").strip()
#
#     ruta = "data/tipos_de_tipos.csv"
#     rows = []
#
#     with open(ruta, "r", encoding="utf-8") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row and row[0] != nombre:
#                 rows.append(row)
#
#     with open(ruta, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)
#
#     return redirect(url_for("configuracion"))
#
#
# @app.route("/add_evento", methods=["POST"])
# def add_evento():
#     nombre = request.form.get("nombre", "").strip()
#     color = request.form.get("color", "").strip()
#
#     if nombre and color:
#         ruta = "data/tipos_de_eventos.csv"
#         with open(ruta, "a", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow([nombre, color])
#
#     return redirect(url_for("configuracion"))
#
#
# @app.route("/edit_evento", methods=["POST"])
# def edit_evento():
#     original = request.form.get("original", "").strip()
#     nombre = request.form.get("nombre", "").strip()
#     color = request.form.get("color", "").strip()
#
#     ruta = "data/tipos_de_eventos.csv"
#     rows = []
#
#     with open(ruta, "r", encoding="utf-8") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row and row[0] == original:
#                 rows.append([nombre, color])
#             else:
#                 rows.append(row)
#
#     with open(ruta, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)
#
#     return redirect(url_for("configuracion"))
#
#
# @app.route("/delete_evento", methods=["POST"])
# def delete_evento():
#     nombre = request.form.get("nombre", "").strip()
#
#     ruta = "data/tipos_de_eventos.csv"
#     rows = []
#
#     with open(ruta, "r", encoding="utf-8") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row and row[0] != nombre:
#                 rows.append(row)
#
#     with open(ruta, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)
#
#     return redirect(url_for("configuracion"))
#
# # ===========================================================
# # FIN CRUD TIPOS DE TIPOS
# # ===========================================================
