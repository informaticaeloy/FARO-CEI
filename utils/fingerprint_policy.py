# utils/fingerprint_policy.py
import json, os
from pathlib import Path

from . import CONFIG_FP_POLICY_JSON

DEFAULT_FP_POLICY = {
    "checks": {
        "visitorId": 60,
        "platform": 10,
        "browser": 10,
        "timezone": 5,
        "deviceMemory": 5,
        "screenResolution": 10
    },
    "confidence_levels": {
        "HIGH": 80,
        "MEDIUM": 50
    }
}


def load_fingerprint_policy() -> dict:
    """
    Carga la política de correlación de fingerprints desde JSON.
    Devuelve una política válida siempre (fallback a defaults).
    """

    if not os.path.exists(CONFIG_FP_POLICY_JSON):
        return DEFAULT_FP_POLICY.copy()

    try:
        with open(CONFIG_FP_POLICY_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        policy = data.get("fingerprint_scoring", {})

        checks = policy.get("checks", {})
        confidence = policy.get("confidence_levels", {})

        # -------- Validación mínima defensiva --------
        if not isinstance(checks, dict) or not checks:
            checks = DEFAULT_FP_POLICY["checks"]

        if not isinstance(confidence, dict):
            confidence = DEFAULT_FP_POLICY["confidence_levels"]

        if "HIGH" not in confidence or "MEDIUM" not in confidence:
            confidence = DEFAULT_FP_POLICY["confidence_levels"]

        return {
            "checks": checks,
            "confidence_levels": confidence
        }

    except Exception:
        # Fail-safe: nunca romper el flujo SOC
        return DEFAULT_FP_POLICY.copy()



def save_fingerprint_policy(policy: dict) -> None:
    """
    Persiste la política de fingerprint en disco.
    Nunca lanza excepción al exterior.
    """

    try:
        data = {
            "fingerprint_scoring": {
                "checks": policy.get("checks", DEFAULT_FP_POLICY["checks"]),
                "confidence_levels": policy.get(
                    "confidence_levels",
                    DEFAULT_FP_POLICY["confidence_levels"]
                )
            }
        }

        # Asegurar directorio
        os.makedirs(os.path.dirname(CONFIG_FP_POLICY_JSON), exist_ok=True)

        with open(CONFIG_FP_POLICY_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception:
        # Fail-safe absoluto: no romper flujo de configuración
        pass
