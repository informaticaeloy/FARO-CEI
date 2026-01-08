# utils package
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

FINGERPRINTS_DIR = os.path.join(DATA_DIR, "fingerprints")
FINGERPRINTS_OLD_DIR = os.path.join(DATA_DIR, "fingerprints_OLD")
FINGERPRINT_BEHAVIOUR_CSV = os.path.join(DATA_DIR, "fingerprint_behavior.csv")
FINGERPRINT_EVENTS_CSV = os.path.join(DATA_DIR, "fingerprint_events.csv")

CONFIG_FP_POLICY_JSON = os.path.join(DATA_DIR, "config_fingerprint.json")

BALIZAS_CSV = os.path.join(DATA_DIR, "balizas.csv")
BALIZAS_EVENTOS_CSV = os.path.join(DATA_DIR, "balizas_eventos.csv")
BALIZAS_FOLDER = os.path.join(BASE_DIR, "balizas")

EVENTOS_CSV = os.path.join(DATA_DIR, "eventos.csv")  # ruta correcta al CSV

ORIGIN_PNG = os.path.join(BALIZAS_FOLDER, "origin.png")

TIPOS_TIPOS_CSV = os.path.join(DATA_DIR, "tipos_de_tipos.csv")
TIPOS_EVENTOS_CSV = os.path.join(DATA_DIR, "tipos_de_eventos.csv")

LOGIN_ATTEMPTS_CSV = os.path.join(DATA_DIR, "login_attempts.csv")

SERVIDORES_CSV = os.path.join(DATA_DIR, "servidores.csv")

ADMIN_FILE = os.path.join(DATA_DIR, "admin.csv")

LOGINS_FILE = os.path.join(DATA_DIR, "login_attempts.csv")

GEOIP_CACHE_FILE = os.path.join(os.path.dirname(__file__), "geoip_cache.json")



