# routes/servidores.py
from flask import Blueprint, request, redirect, url_for
from utils.servidores import cargar_servidores, guardar_servidores

servidores_bp = Blueprint("servidores", __name__)

# ---------- Añadir servidor ----------
@servidores_bp.route("/add_servidor", methods=["POST"])
def add_servidor():
    nombre = request.form.get("nombre", "").strip()
    ruta = request.form.get("ruta", "").strip()
    if nombre and ruta:
        servidores = cargar_servidores()
        servidores.append({"nombre": nombre, "ruta": ruta})
        guardar_servidores(servidores)
    return redirect(url_for("configuracion.config_page"))  # ver nota

# ---------- Editar servidor ----------
@servidores_bp.route("/edit_servidor", methods=["POST"])
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

# ---------- Eliminar servidor ----------
@servidores_bp.route("/delete_servidor", methods=["POST"])
def delete_servidor():
    nombre = request.form.get("nombre", "").strip()
    servidores = [s for s in cargar_servidores() if s["nombre"] != nombre]
    guardar_servidores(servidores)
    return redirect(url_for("configuracion.config_page"))



####################################################################


# ===========================================================
# CRUD SERVIDORES
# ===========================================================
# ---------- Añadir servidor ----------
#
#
# @app.route("/add_servidor", methods=["POST"])
# def add_servidor():
#     nombre = request.form.get("nombre", "").strip()
#     ruta = request.form.get("ruta", "").strip()
#     if nombre and ruta:
#         servidores = cargar_servidores()
#         servidores.append({"nombre": nombre, "ruta": ruta})
#         guardar_servidores(servidores)
#     return redirect(url_for("configuracion"))
#
#
# # ---------- Editar servidor ----------
# @app.route("/edit_servidor", methods=["POST"])
# def edit_servidor():
#     original = request.form.get("original", "").strip()
#     nombre = request.form.get("nombre", "").strip()
#     ruta = request.form.get("ruta", "").strip()
#
#     servidores = cargar_servidores()
#     for s in servidores:
#         if s["nombre"] == original:
#             s["nombre"] = nombre
#             s["ruta"] = ruta
#             break
#     guardar_servidores(servidores)
#     return redirect(url_for("configuracion"))
#
#
# # ---------- Eliminar servidor ----------
# @app.route("/delete_servidor", methods=["POST"])
# def delete_servidor():
#     nombre = request.form.get("nombre", "").strip()
#     servidores = [s for s in cargar_servidores() if s["nombre"] != nombre]
#     guardar_servidores(servidores)
#     return redirect(url_for("configuracion"))