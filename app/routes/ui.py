from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.radio_service import (
    ALLOWED_GROUPS,
    create_station,
    delete_station,
    get_all_stations,
    get_favorite_stations,
    get_station_by_id,
    update_station,
)

ui = Blueprint("ui", __name__)


@ui.route("/")
def home():
    return render_template("home.html", title="Domů")


@ui.route("/radio")
def radio():
    stations = get_all_stations()
    return render_template(
        "radio.html",
        title="Rádio",
        stations=stations,
    )


@ui.route("/favorites")
def favorites():
    stations = get_favorite_stations()
    return render_template(
        "favorites.html",
        title="Oblíbené",
        stations=stations,
    )


@ui.route("/settings")
def settings():
    return render_template("settings.html", title="Nastavení")


@ui.route("/radio/add", methods=["GET", "POST"])
def add_station():
    station = None

    if request.method == "POST":
        form_data = request.form.to_dict(flat=True)
        form_data["is_favorite"] = request.form.get("is_favorite")

        ok, error = create_station(form_data)
        if ok:
            flash("Stanice byla přidána.", "success")
            return redirect(url_for("ui.radio"))

        flash(error, "error")
        station = {
            "name": form_data.get("name", ""),
            "group_name": form_data.get("group_name", "Ostatní"),
            "stream_url": form_data.get("stream_url", ""),
            "logo_url": form_data.get("logo_url", ""),
            "is_favorite": 1 if form_data.get("is_favorite") else 0,
        }

    return render_template(
        "station_form.html",
        title="Přidat stanici",
        station=station,
        groups=ALLOWED_GROUPS,
        form_action=url_for("ui.add_station"),
        submit_label="Uložit stanici",
    )


@ui.route("/radio/<int:station_id>/edit", methods=["GET", "POST"])
def edit_station(station_id: int):
    station = get_station_by_id(station_id)
    if not station:
        flash("Stanice nebyla nalezena.", "error")
        return redirect(url_for("ui.radio"))

    if request.method == "POST":
        form_data = request.form.to_dict(flat=True)
        form_data["is_favorite"] = request.form.get("is_favorite")

        ok, error = update_station(station_id, form_data)
        if ok:
            flash("Stanice byla upravena.", "success")
            return redirect(url_for("ui.radio"))

        flash(error, "error")
        station = {
            "id": station_id,
            "name": form_data.get("name", ""),
            "group_name": form_data.get("group_name", "Ostatní"),
            "stream_url": form_data.get("stream_url", ""),
            "logo_url": form_data.get("logo_url", ""),
            "is_favorite": 1 if form_data.get("is_favorite") else 0,
        }

    return render_template(
        "station_form.html",
        title="Upravit stanici",
        station=station,
        groups=ALLOWED_GROUPS,
        form_action=url_for("ui.edit_station", station_id=station_id),
        submit_label="Uložit změny",
    )


@ui.route("/radio/<int:station_id>/delete", methods=["POST"])
def remove_station(station_id: int):
    delete_station(station_id)
    flash("Stanice byla smazána.", "success")
    return redirect(url_for("ui.radio"))
