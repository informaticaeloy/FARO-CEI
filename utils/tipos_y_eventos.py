# utils/tipos_y_eventos.py
import os
import csv

# ---------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------

from . import TIPOS_TIPOS_CSV, TIPOS_EVENTOS_CSV, DATA_DIR


# Garantiza que el directorio de datos exista
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# TIPOS
# ---------------------------------------------------------------------

def cargar_tipos_de_tipos():
    """
    Carga los tipos desde CSV.
    Devuelve: [{nombre, color}, ...]
    """
    tipos = []

    if not os.path.exists(TIPOS_TIPOS_CSV):
        return tipos

    with open(TIPOS_TIPOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 2:
                continue

            nombre, color = row
            tipos.append({
                "nombre": nombre.strip(),
                "color": color.strip()
            })

    return tipos


def guardar_tipos_de_tipos(tipos):
    """
    Sobrescribe el CSV de tipos.
    """
    with open(TIPOS_TIPOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for t in tipos:
            writer.writerow([t["nombre"], t["color"]])


def crear_tipo(form):
    """
    Alta de nuevo tipo.
    """
    nombre = form.get("nombre", "").strip()
    color = form.get("color", "").strip()

    if not nombre:
        return

    tipos = cargar_tipos_de_tipos()
    tipos.append({"nombre": nombre, "color": color})
    guardar_tipos_de_tipos(tipos)


def editar_tipo(form):
    """
    Edición de tipo existente.
    """
    original = form.get("original", "").strip()
    nombre = form.get("nombre", "").strip()
    color = form.get("color", "").strip()

    if not original or not nombre:
        return

    tipos = cargar_tipos_de_tipos()
    for t in tipos:
        if t["nombre"] == original:
            t["nombre"] = nombre
            t["color"] = color
            break

    guardar_tipos_de_tipos(tipos)


def eliminar_tipo(form):
    """
    Eliminación de tipo.
    """
    nombre = form.get("nombre", "").strip()
    if not nombre:
        return

    tipos = cargar_tipos_de_tipos()
    tipos = [t for t in tipos if t["nombre"] != nombre]
    guardar_tipos_de_tipos(tipos)


# ---------------------------------------------------------------------
# EVENTOS
# ---------------------------------------------------------------------

def cargar_tipos_de_eventos():
    """
    Carga los tipos de eventos desde CSV.
    """
    eventos = []

    if not os.path.exists(TIPOS_EVENTOS_CSV):
        return eventos

    with open(TIPOS_EVENTOS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 2:
                continue

            nombre, color = row
            eventos.append({
                "nombre": nombre.strip(),
                "color": color.strip()
            })

    return eventos


def guardar_tipos_de_eventos(eventos):
    """
    Sobrescribe el CSV de eventos.
    """
    with open(TIPOS_EVENTOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for e in eventos:
            writer.writerow([e["nombre"], e["color"]])


def crear_evento(form):
    """
    Alta de evento.
    """
    nombre = form.get("nombre", "").strip()
    color = form.get("color", "").strip()

    if not nombre:
        return

    eventos = cargar_tipos_de_eventos()
    eventos.append({"nombre": nombre, "color": color})
    guardar_tipos_de_eventos(eventos)


def editar_evento(form):
    """
    Edición de evento.
    """
    original = form.get("original", "").strip()
    nombre = form.get("nombre", "").strip()
    color = form.get("color", "").strip()

    if not original or not nombre:
        return

    eventos = cargar_tipos_de_eventos()
    for e in eventos:
        if e["nombre"] == original:
            e["nombre"] = nombre
            e["color"] = color
            break

    guardar_tipos_de_eventos(eventos)


def eliminar_evento(form):
    """
    Eliminación de evento.
    """
    nombre = form.get("nombre", "").strip()
    if not nombre:
        return

    eventos = cargar_tipos_de_eventos()
    eventos = [e for e in eventos if e["nombre"] != nombre]
    guardar_tipos_de_eventos(eventos)
