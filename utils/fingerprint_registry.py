# routes/fingerprint_registry.py

import os
import json
import csv
import uuid
from datetime import datetime
from collections import defaultdict
from utils.fingerprint_policy import load_fingerprint_policy

# ---------------------------
# Rutas base
# ---------------------------

from . import FINGERPRINTS_DIR, BALIZAS_EVENTOS_CSV


# ---------------------------
# Carga de fingerprints
# ---------------------------
def cargar_fingerprints():
    """
    Carga todos los fingerprints almacenados en disco.
    """
    fps = []

    if not os.path.isdir(FINGERPRINTS_DIR):
        return fps

    for fname in os.listdir(FINGERPRINTS_DIR):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(FINGERPRINTS_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                fps.append(json.load(f))
        except Exception:
            continue

    return fps


def cargar_fingerprint(fingerprint_id: str):
    """
    Devuelve un fingerprint concreto por ID.
    """
    path = os.path.join(FINGERPRINTS_DIR, f"{fingerprint_id}.json")
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------
# Comparación fingerprints
# ---------------------------
def comparar_fingerprints(fp1: dict, fp2: dict) -> dict:
    """
    Compara dos fingerprints usando la política configurable
    y devuelve score, coincidencias, diferencias y nivel de confianza.
    """
    policy = load_fingerprint_policy()

    checks: dict = policy.get("checks", {})
    confidence_levels: dict = policy.get("confidence_levels", {})

    score = 0
    matches = []
    mismatches = []

    def get_signal(fp, key):
        return fp.get("signals", {}).get(key)

    # -----------------------------
    # Evaluación de señales
    # -----------------------------
    for key, weight in checks.items():
        v1 = get_signal(fp1, key)
        v2 = get_signal(fp2, key)

        if v1 is not None and v1 == v2:
            score += int(weight)
            matches.append(key)
        else:
            mismatches.append({
                "field": key,
                "fp1": v1,
                "fp2": v2
            })

    # -----------------------------
    # Clasificación de confianza
    # -----------------------------
    high_threshold = confidence_levels.get("HIGH", 80)
    medium_threshold = confidence_levels.get("MEDIUM", 50)

    if score >= high_threshold:
        confidence = "HIGH"
    elif score >= medium_threshold:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "score": score,
        "confidence": confidence,
        "matches": matches,
        "mismatches": mismatches,
        "policy_used": {
            "checks": checks,
            "confidence_levels": confidence_levels
        }
    }
# def comparar_fingerprints(fp1: dict, fp2: dict):
#     """
#     Compara dos fingerprints y devuelve score de similitud.
#     """
#     score = 0
#     matches = []
#     mismatches = []
#
#     def get_signal(fp, key):
#         return fp.get("signals", {}).get(key)
#
#     checks = [
#         ("visitorId", 60),
#         ("platform", 10),
#         ("browser", 10),
#         ("timezone", 5),
#         ("deviceMemory", 5),
#         ("screenResolution", 10),
#     ]
#
#     for key, weight in checks:
#         v1 = get_signal(fp1, key)
#         v2 = get_signal(fp2, key)
#
#         if v1 is not None and v1 == v2:
#             score += weight
#             matches.append(key)
#         else:
#             mismatches.append((key, v1, v2))
#
#     return {
#         "score": score,
#         "matches": matches,
#         "mismatches": mismatches,
#         "confidence": (
#             "HIGH" if score >= 80 else
#             "MEDIUM" if score >= 50 else
#             "LOW"
#         )
#     }


# ---------------------------
# Listado fingerprints
# ---------------------------
def listar_fingerprints():
    """
    Devuelve dict {fingerprint_id: metadata}
    """
    fps = {}

    if not os.path.isdir(FINGERPRINTS_DIR):
        return fps

    for fname in os.listdir(FINGERPRINTS_DIR):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(FINGERPRINTS_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            fp_id = data.get("fingerprint_id")
            if fp_id:
                fps[fp_id] = {
                    "fingerprint_id": fp_id,
                    "latest": data,
                    "captures": []
                }
        except Exception:
            continue

    return fps


# ---------------------------
# Correlación con balizas
# ---------------------------
def eventos_por_fingerprint(fingerprint_id: str):
    """
    Devuelve todos los eventos asociados a un fingerprint.
    """
    eventos = []

    if not os.path.exists(BALIZAS_EVENTOS_CSV):
        return eventos

    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("fingerprint_id") == fingerprint_id:
                eventos.append(row)

    return eventos



def correlacionar_fingerprints_balizas_desde_fps(fps: dict):
    """
    Enlaza fingerprints con eventos de balizas.
    """
    stats = {}

    for fp_id in fps.keys():
        stats[fp_id] = {
            "total_visitas": 0,
            "balizas": {},
            "ultima_visita": None
        }
    if not os.path.exists(BALIZAS_EVENTOS_CSV):
        return stats

    with open(BALIZAS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fp_id = row.get("fingerprint_id")
            if fp_id not in stats:
                continue

            stats[fp_id]["total_visitas"] += 1

            origen = row.get("origen", "desconocido")
            stats[fp_id]["balizas"][origen] = (
                stats[fp_id]["balizas"].get(origen, 0) + 1
            )

            ts = row.get("timestamp")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", ""))
                    if (
                        not stats[fp_id]["ultima_visita"]
                        or dt > stats[fp_id]["ultima_visita"]
                    ):
                        stats[fp_id]["ultima_visita"] = dt
                except Exception:
                    pass

    return stats
