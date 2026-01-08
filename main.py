#!/usr/bin/env python3
"""
Main entrypoint de la aplicación SOC Dashboard.
Depurado para producción: solo bootstrap, Blueprints y filtros Jinja.
Toda la lógica y endpoints están en routes/.
"""

import os
import csv
from flask import Flask
from utils.utils import formatear_timestamp_es, calcular_texto, format_duration
from utils.geoip import country_code_to_emoji

# ---------------------------
# Importar Blueprints
# ---------------------------
from routes.balizas import balizas_bp
from routes.equipos import equipos_bp
from routes.auth import auth_bp
from routes.webhook import webhook_bp
from routes.servidores import servidores_bp
from routes.configuracion import configuracion_bp
from routes.logins import logins_bp
from routes.dashboard import dashboard_bp
from routes.soc import soc_bp
from routes.fingerprint import fingerprint_bp
from routes.fingerprint_engines import fingerprint_engines_bp


# ---------------------------
# Inicialización Flask
# ---------------------------
# app = Flask("soc_dashboard", template_folder="templates", static_folder="static")
app = Flask(
    "faro_cei",
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)
app.secret_key = "06b88d71-94fc-4040-a429-c946271c7427"

# ---------------------------
# Registro Blueprints
# ---------------------------
blueprints = [
    balizas_bp, equipos_bp, auth_bp, webhook_bp, servidores_bp,
    configuracion_bp, logins_bp, dashboard_bp, soc_bp,
    fingerprint_bp, fingerprint_engines_bp
]

for bp in blueprints:
    app.register_blueprint(bp)

# ---------------------------
# Filtros y funciones globales Jinja
# ---------------------------
app.jinja_env.filters['fecha_es'] = formatear_timestamp_es
app.jinja_env.filters['format_duration'] = format_duration

@app.template_filter('flag')
def flag_filter(country_code):
    return country_code_to_emoji(country_code)

app.jinja_env.globals.update(calcular_texto=calcular_texto)

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    # print("############################################")
    # print("### INICIO DE LA IMPRESION DE LOS ROUTES ###")
    # print("############################################")
    # for rule in app.url_map.iter_rules():
    #    print(rule.endpoint, rule)
    # print("###########################################")
    # print("###  FIN DE LA IMPRESION DE LOS ROUTES  ###")
    # print("###########################################")

    app.run(host="0.0.0.0", port=8000, debug=False)


