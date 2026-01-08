# routes/auth.py
from flask import Blueprint, request, session, redirect, url_for, render_template
from utils.logins import (
    cargar_admin,
    log_login_attempt,
    log_event_block,
    get_client_ip,
    check_brute_force,
    BLOQUEO_MINUTOS,
    parse_user_agent
)
from utils.utils import obtener_ip_hostname
from utils.auth import validar_password_segura, actualizar_password_admin
from utils.security import verify_password, hash_password

auth_bp = Blueprint("auth", __name__)

# ---------- LOGIN ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    admin_cfg = cargar_admin()

    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        # Info host local
        host_info = obtener_ip_hostname()
        ip_local = host_info.get("ip_local", "")
        hostname_local = host_info.get("hostname_local", "")

        ip = get_client_ip()
        user_agent = request.headers.get("User-Agent", "")

        # Brute-force check
        if check_brute_force(user, ip):
            os_guess, browser_guess = parse_user_agent(user_agent)
            log_event_block(
                username=user,
                password=pwd,
                ip=ip,
                user_agent=user_agent,
                os_name=os_guess,
                navegador=browser_guess,
                ip_local=ip_local,
                hostname_local=hostname_local,
                motivo="BRUTEFORCE"
            )
            return render_template(
                "login.html",
                error=f"Demasiados intentos fallidos. Intenta en {BLOQUEO_MINUTOS} minutos"
            )

        # Login correcto
        # if user == admin_cfg["username"] and pwd == admin_cfg["password"]:
        if (
                    user == admin_cfg["username"] and
                    verify_password(pwd, admin_cfg["password"])
        ):
            log_login_attempt(
                username=user,
                password=pwd,
                result="success",
                ip_local=ip_local,
                hostname_local=hostname_local
            )
            session["user"] = user
            # Forzar cambio de contraseña si credenciales débiles
            if user == "usuario" and pwd == "usuario":
                session["force_password_change"] = True
                return redirect(url_for("auth.force_change_password"))

            return redirect(url_for("dashboard.admin"))

        # Login fallido
        log_login_attempt(
            username=user,
            password=pwd,
            result="failure",
            ip_local=ip_local,
            hostname_local=hostname_local
        )
        return render_template("login.html", error="Credenciales inválidas")

    return render_template("login.html", error=None)


# ---------- LOGOUT ----------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ---------- FORCE PASSWORD CHANGE ----------
@auth_bp.route("/force-change-password", methods=["GET", "POST"])
def force_change_password():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    if not session.get("force_password_change"):
        return redirect(url_for("dashboard.admin"))

    error = None
    success = None

    if request.method == "POST":
        pwd1 = request.form.get("password")
        pwd2 = request.form.get("password_confirm")

        if pwd1 != pwd2:
            error = "Las contraseñas no coinciden"
        else:
            ok, msg = validar_password_segura(pwd1)
            if not ok:
                error = msg
            else:
                actualizar_password_admin(pwd1)

                # Limpieza del estado forzado
                session.pop("force_password_change", None)

                # Log de evento de seguridad
                log_event_block(
                    username=session.get("user"),
                    password="***",
                    ip=get_client_ip(),
                    user_agent=request.headers.get("User-Agent", ""),
                    os_name="",
                    navegador="",
                    ip_local="",
                    hostname_local="",
                    motivo="PASSWORD_CHANGE_DEFAULT"
                )
                return redirect(url_for("dashboard.admin"))

    return render_template(
        "force_change_password.html",
        error=error,
        success=success
    )



