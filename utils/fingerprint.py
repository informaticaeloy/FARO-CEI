import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Tuple

from . import FINGERPRINTS_DIR, BASE_DIR

def calcular_hash_estable(core_signals: Dict) -> str:
    """
    Calcula hash estable v1 de señales core (no volátiles).

    Args:
        core_signals: dict con señales básicas de fingerprint.

    Returns:
        Hash SHA256 hexadecimal.
    """
    canonical = json.dumps(core_signals, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def guardar_fingerprint(payload: Dict, source: Dict) -> Tuple[str, bool]:
    engines = payload.get("engines", {})
    fpjs = engines.get("fingerprintjs", {})

    # Asegurarnos de usar los datos reales devueltos por el adapter
    fpjs_data = fpjs.get("data", {})  # <-- aquí están visitorId y components

    # Señales core para hash, extraídas del objeto 'data'
    core = {
        "visitorId": fpjs_data.get("visitorId"),
        "browserName": fpjs_data.get("components", {}).get("browserName", None),
        "browserVersion": fpjs_data.get("components", {}).get("browserVersion", None),
        "os": fpjs_data.get("components", {}).get("os", None),
        "osVersion": fpjs_data.get("components", {}).get("osVersion", None),
        "platform": fpjs_data.get("components", {}).get("platform", None),
        "device": fpjs_data.get("components", {}).get("device", None),
        "hardwareConcurrency": fpjs_data.get("components", {}).get("hardwareConcurrency", None),
        "deviceMemory": fpjs_data.get("components", {}).get("deviceMemory", None),
    }

    # print("INICIO CORE")
    # print("============================================================")
    # print(core)
    # print("============================================================")
    # print("FIN CORE")

    hash_estable = calcular_hash_estable(core)
    fingerprint_id = f"fp_{hash_estable[:16]}"
    path = os.path.join(FINGERPRINTS_DIR, f"{fingerprint_id}.json")
    es_nuevo = not os.path.exists(path)

    print(f"[FP] {'NUEVO' if es_nuevo else 'YA EXISTENTE'} fingerprint → {fingerprint_id}")

    data = {
        "fingerprint_id": fingerprint_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": source,
        "hash": {
            "stable": hash_estable,
            "strategy": "v1-core"
        },
        "signals": {
            "core": core,
            "extended": fpjs
        },
        "raw": payload
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return fingerprint_id, es_nuevo
