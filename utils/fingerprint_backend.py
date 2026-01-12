# utils/fingerprint_backend.py

import os
import json
import hashlib
from datetime import datetime

# ---------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------

from . import  BASE_DIR, FINGERPRINTS_DIR

# Asegura la existencia del directorio de fingerprints
os.makedirs(FINGERPRINTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# Normalización mínima para hash estable
# ---------------------------------------------------------------------

def _canonical_fingerprint(fp: dict) -> dict:
    """
    Extrae únicamente señales consideradas estables para el cálculo del hash.
    El fingerprint completo se persiste, pero el identificador se basa solo en
    este subconjunto para evitar colisiones por señales volátiles.
    """

    engines = fp.get("engines", {}) or {}
    fpjs = engines.get("fingerprintjs", {}) or {}

    data = fpjs.get("data", {}) or {}
    components = data.get("components", {}) or {}

    return {
        # Metadatos generales
        "ua": fp.get("metadata", {}).get("user_agent"),

        # Señales fingerprintjs consideradas estables
        "visitorId": data.get("visitorId"),
        "platform": components.get("platform", {}).get("value"),
        "hardwareConcurrency": components.get("hardwareConcurrency", {}).get("value"),
        "deviceMemory": components.get("deviceMemory", {}).get("value"),
        "timezone": components.get("timezone", {}).get("value"),
        "languages": components.get("languages", {}).get("value"),
        "screenResolution": components.get("screenResolution", {}).get("value"),
    }


def fingerprint_hash(fp: dict) -> str:
    """
    Calcula el hash SHA-256 estable a partir del fingerprint canonizado.
    El JSON se serializa de forma determinista.
    """

    canonical = _canonical_fingerprint(fp)
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------

def store_fingerprint(fp: dict) -> str:
    """
    Guarda el fingerprint completo en disco si no existe.
    Si ya existe, actualiza únicamente el campo last_seen.

    Devuelve:
        fingerprint_id (hash estable)
    """

    fp_id = fingerprint_hash(fp)
    path = os.path.join(FINGERPRINTS_DIR, f"{fp_id}.json")
    now = datetime.utcnow().isoformat() + "Z"

    if not os.path.exists(path):
        # Primer avistamiento del fingerprint
        payload = {
            "fingerprint_id": fp_id,
            "first_seen": now,
            "last_seen": now,
            "data": fp
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    else:
        # Fingerprint ya conocido → solo se actualiza last_seen
        try:
            with open(path, "r+", encoding="utf-8") as f:
                payload = json.load(f)
                payload["last_seen"] = now
                f.seek(0)
                json.dump(payload, f, indent=2)
                f.truncate()
        except Exception:
            # Fallo silencioso: no rompe ingestión
            pass

    return fp_id
