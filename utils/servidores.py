# utils/servidores.py
import os
import csv
from . import BASE_DIR, DATA_DIR, SERVIDORES_CSV


def cargar_servidores() -> list[dict]:
    """
    Carga la lista de servidores desde el CSV.

    Cada servidor se representa como un diccionario:
        {
            "nombre": str,
            "ruta": str
        }

    Devuelve lista vacía si el archivo no existe.
    """
    servidores = []

    if os.path.exists(SERVIDORES_CSV):
        try:
            with open(SERVIDORES_CSV, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        servidores.append({"nombre": row[0], "ruta": row[1]})
        except Exception as e:
            print(f"[!] Error leyendo {SERVIDORES_CSV}: {e}")

    return servidores


def guardar_servidores(servidores: list[dict]):
    """
    Guarda la lista de servidores en el CSV.

    Cada elemento de `servidores` debe ser un dict con keys:
        - nombre
        - ruta
    """
    os.makedirs(os.path.dirname(SERVIDORES_CSV), exist_ok=True)

    try:
        with open(SERVIDORES_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for s in servidores:
                writer.writerow([s.get("nombre", ""), s.get("ruta", "")])
    except Exception as e:
        print(f"[!] Error escribiendo {SERVIDORES_CSV}: {e}")
