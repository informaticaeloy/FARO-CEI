# routes/fingerprint_engines.py
from flask import Blueprint, request, jsonify
import csv, json
import uuid
from datetime import datetime

FINGERPRINT_EVENTS_CSV = "data/fingerprint_events.csv"  # define ruta

fingerprint_engines_bp = Blueprint("fingerprint_engines", __name__)

# -----------------------
# Helpers internos
# -----------------------
def save_fingerprint_event(fp_id, baliza_id, timestamp, confidence, engines, metadata):
    with open(FINGERPRINT_EVENTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            fp_id,
            baliza_id,
            confidence,
            json.dumps(engines, ensure_ascii=False),
            metadata.get("user_agent"),
            metadata.get("timezone"),
            metadata.get("screen"),
            metadata.get("platform")
        ])

def normalize_engines(engines_raw):
    # tu lógica aquí
    return engines_raw

def calculate_fp_id(engines, metadata):
    # tu lógica aquí
    return str(uuid.uuid4())

def calculate_confidence(engines):
    # tu lógica aquí
    return 0.95

# -----------------------
# Endpoint
# -----------------------
@fingerprint_engines_bp.route("/webhook/fingerprint", methods=["POST"])
def collect_fingerprint_webhook():
    data = request.get_json(force=True)

    baliza_id = data.get("baliza_id")
    ts = data.get("timestamp") or datetime.utcnow().isoformat() + "Z"
    fingerprint = data.get("fingerprint", {})

    metadata = fingerprint.get("metadata", {})
    engines_raw = fingerprint.get("engines", {})

    engines = normalize_engines(engines_raw)
    fp_id = calculate_fp_id(engines, metadata)
    confidence = calculate_confidence(engines)

    save_fingerprint_event(
        fp_id=fp_id,
        baliza_id=baliza_id,
        timestamp=ts,
        confidence=confidence,
        engines=engines,
        metadata=metadata
    )

    return jsonify({
        "status": "ok",
        "fp_id": fp_id,
        "confidence": confidence
    })



# # ------------------------------------------------------------------------------------
# # --------------------------------------------------------  FINGERPRINT VARIOS MOTORES
# # ------------------------------------------------------------------------------------
# @app.route("/webhook/fingerprint", methods=["POST"])
# def collect_fingerprint_webhook():
#     data = request.get_json(force=True)
#
#     baliza_id = data.get("baliza_id")
#     ts = data.get("timestamp")
#     fingerprint = data.get("fingerprint", {})
#
#     metadata = fingerprint.get("metadata", {})
#     engines_raw = fingerprint.get("engines", {})
#
#     engines = normalize_engines(engines_raw)
#     fp_id = calculate_fp_id(engines, metadata)
#     confidence = calculate_confidence(engines)
#
#     save_fingerprint_event(
#         fp_id=fp_id,
#         baliza_id=baliza_id,
#         timestamp=ts,
#         confidence=confidence,
#         engines=engines,
#         metadata=metadata
#     )
#
#     return jsonify({
#         "status": "ok",
#         "fp_id": fp_id,
#         "confidence": confidence
#     })
#
#
# def save_fingerprint_event(fp_id, baliza_id, timestamp, confidence, engines, metadata):
#     with open(FINGERPRINT_EVENTS_CSV, "a", encoding="utf-8", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             timestamp,
#             fp_id,
#             baliza_id,
#             confidence,
#             json.dumps(engines, ensure_ascii=False),
#             metadata.get("user_agent"),
#             metadata.get("timezone"),
#             metadata.get("screen"),
#             metadata.get("platform")
#         ])
#
# # ------------------------------------------------------------------------------------
# # ----------------------------------------------------- FIN FINGERPRINT VARIOS MOTORES
# # ------------------------------------------------------------------------------------