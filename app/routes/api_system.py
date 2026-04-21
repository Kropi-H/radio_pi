import subprocess
from pathlib import Path

from flask import Blueprint, current_app, jsonify

api_system = Blueprint("api_system", __name__, url_prefix="/api/system")


def run_script(script_name: str) -> tuple[bool, str]:
    project_root = Path(current_app.config["PROJECT_ROOT"])
    script_path = project_root / "scripts" / script_name

    if not script_path.exists():
        return False, f"Skript neexistuje: {script_path}"

    try:
        subprocess.Popen(
            ["sudo", str(script_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, "OK"
    except Exception as exc:
        return False, str(exc)


@api_system.route("/close-ui", methods=["POST"])
def close_ui():
    ok, msg = run_script("close_ui.sh")
    status_code = 200 if ok else 500
    return jsonify({"ok": ok, "message": msg}), status_code


@api_system.route("/restart-ui", methods=["POST"])
def restart_ui():
    ok, msg = run_script("restart_ui.sh")
    status_code = 200 if ok else 500
    return jsonify({"ok": ok, "message": msg}), status_code


@api_system.route("/reboot", methods=["POST"])
def reboot():
    ok, msg = run_script("reboot_pi.sh")
    status_code = 200 if ok else 500
    return jsonify({"ok": ok, "message": msg}), status_code


@api_system.route("/shutdown", methods=["POST"])
def shutdown():
    ok, msg = run_script("shutdown_pi.sh")
    status_code = 200 if ok else 500
    return jsonify({"ok": ok, "message": msg}), status_code


@api_system.route("/display-off", methods=["POST"])
def display_off():
    ok, msg = run_script("display_off.sh")
    status_code = 200 if ok else 500
    return jsonify({"ok": ok, "message": msg}), status_code
