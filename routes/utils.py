# routes/utils.py

from flask import Blueprint, request, jsonify
import socket

utils_bp = Blueprint("utils", __name__)

# -----------------------------------------------------------------
# UTILS · HOST INFO (DIAGNÓSTICO)
# -----------------------------------------------------------------
@utils_bp.route("/test_hostinfo", methods=["GET"])
def test_hostinfo():
    """
    Endpoint de diagnóstico.
    Devuelve IP efectiva y reverse DNS si existe.
    """
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "Desconocida"

    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        hostname = "No disponible"

    return jsonify({
        "ip": ip,
        "hostname": hostname
    })




# # --------------------------------------- OBTENER INFORMACION DE PC
# @app.route("/test_hostinfo")
# def test_hostinfo():
#     # Obtener IP real del cliente
#     ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "Desconocida"
#
#     # Intentar hacer reverse DNS
#     try:
#         hostname = socket.gethostbyaddr(ip)[0]
#     except Exception:
#         hostname = "No disponible"
#
#     return jsonify({
#         "ip": ip,
#         "hostname": hostname
#     })