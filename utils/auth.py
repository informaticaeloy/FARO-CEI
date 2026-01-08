# routes/auth.py

"""
Módulo de autenticación básico.
Proporciona funciones para gestionar sesiones de usuario y controlar
el acceso a rutas que requieren login.
"""

from flask import session
from utils.security import hash_password
from utils.logins import cargar_admin
from . import ADMIN_FILE
import re
import csv


# -----------------------------------------------------------------
# Función de comprobación de sesión
# -----------------------------------------------------------------
def requiere_login():
    """
    Comprueba si hay un usuario autenticado en la sesión actual.

    Retorna:
        bool: True si el usuario está logueado (clave "user" en session),
              False en caso contrario.

    Uso típico:
        if not requiere_login():
            return redirect(url_for("auth.login"))
    """
    return "user" in session


def validar_password_segura(password: str) -> tuple[bool, str]:
    """
    Política mínima de complejidad:
    - ≥ 10 caracteres
    - 1 mayúscula
    - 1 minúscula
    - 1 número
    - 1 símbolo
    """
    if len(password) < 10:
        return False, "Debe tener al menos 10 caracteres"

    if not re.search(r"[A-Z]", password):
        return False, "Debe contener al menos una letra mayúscula"

    if not re.search(r"[a-z]", password):
        return False, "Debe contener al menos una letra minúscula"

    if not re.search(r"[0-9]", password):
        return False, "Debe contener al menos un número"

    if not re.search(r"[^\w\s]", password):
        return False, "Debe contener al menos un símbolo"

    return True, ""


def actualizar_password_admin(nueva_password: str, username: str = "usuario"):
    """Actualiza la contraseña del admin en el CSV"""
    admin = {"username": username, "password": nueva_password}

    with open(ADMIN_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=admin.keys())
        writer.writeheader()
        writer.writerow(admin)
# def actualizar_password_admin(nueva_password: str):
#     admin = cargar_admin()
#
#     admin["password"] = hash_password(nueva_password)
#
#     with open(ADMIN_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=admin.keys())
#         writer.writeheader()
#         writer.writerow(admin)
