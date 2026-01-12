# routes/webhook.py
from flask import Blueprint, request
from utils.webhook_handler import procesar_webhook

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET","POST"], endpoint="webhook")
def webhook_route():
    print("[DEBUG] /webhook llamada")  # <-- print inicial
    print(f"[DEBUG] Request args: {request.args}")  # muestra los parámetros GET
    print(f"[DEBUG] Request form: {request.form}")  # si fuera POST form
    print(f"[DEBUG] Request JSON: {request.get_json(silent=True)}")  # si fuera POST JSON
    return procesar_webhook()
