from flask import Blueprint, current_app, jsonify, request

from app.services.radio_service import get_station_by_id
from app.services.settings_service import set_setting

api_player = Blueprint("api_player", __name__, url_prefix="/api/player")


def _persist_status(status: dict) -> None:
    volume = status.get("volume")
    if volume is not None:
        set_setting("player.volume", str(volume))

    station_id = status.get("station_id")
    if station_id:
        set_setting("player.last_station_id", str(station_id))
    else:
        set_setting("player.last_station_id", "")


@api_player.route("/status", methods=["GET"])
def status():
    return jsonify(current_app.audio_service.status())


@api_player.route("/play/<int:station_id>", methods=["POST"])
def play_station(station_id: int):
    station = get_station_by_id(station_id)
    if not station:
        return jsonify({"ok": False, "error": "Stanice nebyla nalezena."}), 404

    current_app.audio_service.play(
        station_id=station["id"],
        name=station["name"],
        group_name=station["group_name"],
        url=station["stream_url"],
    )

    status = current_app.audio_service.status()
    _persist_status(status)

    return jsonify({
        "ok": True,
        "message": "Přehrávání spuštěno.",
        "status": status,
    })


@api_player.route("/stop", methods=["POST"])
def stop():
    current_app.audio_service.stop()
    status = current_app.audio_service.status()
    _persist_status(status)
    return jsonify({
        "ok": True,
        "message": "Přehrávání zastaveno.",
        "status": status,
    })


@api_player.route("/pause", methods=["POST"])
def pause():
    current_app.audio_service.pause()
    status = current_app.audio_service.status()
    return jsonify({
        "ok": True,
        "message": "Přehrávání pozastaveno.",
        "status": status,
    })


@api_player.route("/resume", methods=["POST"])
def resume():
    current_app.audio_service.resume()
    status = current_app.audio_service.status()
    return jsonify({
        "ok": True,
        "message": "Přehrávání obnoveno.",
        "status": status,
    })


@api_player.route("/pause-toggle", methods=["POST"])
def pause_toggle():
    current_app.audio_service.toggle_pause()
    status = current_app.audio_service.status()
    return jsonify({
        "ok": True,
        "message": "Přepnuto.",
        "status": status,
    })


@api_player.route("/volume", methods=["POST"])
def set_volume():
    data = request.get_json(silent=True) or {}
    volume = data.get("volume")

    if volume is None:
        return jsonify({"ok": False, "error": "Chybí volume."}), 400

    try:
        volume = int(volume)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Volume musí být číslo."}), 400

    current_app.audio_service.set_volume(volume)
    status = current_app.audio_service.status()
    _persist_status(status)

    return jsonify({
        "ok": True,
        "message": "Hlasitost nastavena.",
        "status": status,
    })
