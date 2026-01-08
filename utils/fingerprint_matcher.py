import os
import json

# Campos utilizados para la comparación básica de fingerprints
# Todos tienen el mismo peso en este matcher
CAMPOS_CLAVE = [
    "visitorId",
    "platform",
    "browser",
    "timezone",
    "deviceMemory",
    "screenResolution"
]


def comparar_fingerprints(fp1_path: str, fp2_path: str) -> dict:
    """
    Compara dos fingerprints almacenados en disco.
    Devuelve un score porcentual y el detalle de coincidencias.
    Diseñado como matcher simple (no ponderado).
    """

    try:
        with open(fp1_path, "r", encoding="utf-8") as f:
            fp1 = json.load(f)

        with open(fp2_path, "r", encoding="utf-8") as f:
            fp2 = json.load(f)

    except Exception as e:
        # Fallo controlado: no rompe el flujo del sistema
        return {
            "score": 0,
            "matches": [],
            "mismatches": [],
            "error": str(e)
        }

    raw1 = fp1.get("raw", {})
    raw2 = fp2.get("raw", {})

    matches = []
    mismatches = []

    score = 0
    total = len(CAMPOS_CLAVE)

    for campo in CAMPOS_CLAVE:
        val1 = raw1.get(campo)
        val2 = raw2.get(campo)

        if val1 is not None and val1 == val2:
            matches.append((campo, val1))
            score += 1
        else:
            mismatches.append((campo, val1, val2))

    porcentaje = int((score / total) * 100) if total else 0

    return {
        "score": porcentaje,
        "matches": matches,
        "mismatches": mismatches
    }


def cargar_fingerprints(directorio: str) -> list:
    """
    Devuelve una lista de rutas absolutas a fingerprints JSON.
    No valida contenido, solo presencia en disco.
    """

    if not os.path.isdir(directorio):
        return []

    fingerprints = []

    for fname in os.listdir(directorio):
        if fname.endswith(".json"):
            fingerprints.append(os.path.join(directorio, fname))

    return fingerprints
