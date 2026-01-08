import hashlib
from typing import Dict, Any

ENGINE_WEIGHTS: Dict[str, float] = {
    "fingerprintjs": 0.40,
    "creepjs": 0.30,
    "broprint": 0.15,
    "thumbmark": 0.10,
    "detectincognito": 0.05
}

def normalize_engines(engines: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza los resultados de los distintos motores de fingerprint.
    Convierte valores vacíos, None o errores a None, el resto a string.
    """
    normalized = {}
    for engine, value in engines.items():
        if value in (None, "", False):
            normalized[engine] = None
        elif isinstance(value, dict) and value.get("error"):
            normalized[engine] = None
        else:
            normalized[engine] = str(value)
    return normalized


def calculate_confidence(engines: Dict[str, Any]) -> float:
    """
    Calcula la confianza total combinando los motores con sus pesos.
    Devuelve un float entre 0 y 1 con dos decimales.
    """
    confidence = 0.0
    for engine, weight in ENGINE_WEIGHTS.items():
        if engines.get(engine):
            confidence += weight
    return round(confidence, 2)


def calculate_fp_id(engines: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """
    Calcula un ID único de fingerprint basado en los valores de engines y metadata.
    Devuelve un string tipo 'fp_<hash16>'.
    """
    base = (
        (engines.get("fingerprintjs") or "") +
        (engines.get("creepjs") or "") +
        (metadata.get("user_agent") or "") +
        (metadata.get("timezone") or "")
    )
    return "fp_" + hashlib.sha256(base.encode()).hexdigest()[:16]
