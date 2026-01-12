# utils/security.py
from werkzeug.security import generate_password_hash, check_password_hash


# def hash_password(password: str) -> str:
#     """
#     Genera un hash seguro de la contraseña.
#     Algoritmo: PBKDF2 + SHA256 (estándar Flask)
#     """
#     return generate_password_hash(
#         password,
#         method="pbkdf2:sha256",
#         salt_length=16
#     )
#
#
# def verify_password(password: str, hashed: str) -> bool:
#     """
#     Verifica una contraseña en claro contra su hash almacenado
#     """
#     return check_password_hash(
#         hashed,
#         password
#     )


def hash_password(password: str) -> str:
    """Devuelve la contraseña hasheada"""
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Comprueba si la contraseña coincide con el hash"""
    return check_password_hash(hashed, password)