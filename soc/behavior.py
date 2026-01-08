import csv
import os
from flask import jsonify, request

# --- Rutas (localizadas solo aquí) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

DATA_FOLDER = os.path.join(BASE_DIR, "data")
FINGERPRINT_BEHAVIOR_CSV = os.path.join(DATA_FOLDER, "fingerprint_behavior.csv")

# ---------------------------
# Handler SOC
# ---------------------------
def soc_behavior_handler():
    classification = request.args.get("classification")
    is_tor = request.args.get("is_tor")

    if not os.path.exists(FINGERPRINT_BEHAVIOR_CSV):
        return jsonify({"error": "behavior data not generated"}), 404

    results = []

    with open(FINGERPRINT_BEHAVIOR_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if classification and row["classification"] != classification:
                continue
            if is_tor is not None and row["is_tor"] != is_tor:
                continue
            results.append(row)

    return jsonify({
        "total": len(results),
        "results": results
    })
