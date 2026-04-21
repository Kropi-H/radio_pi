from urllib.parse import urlparse

from app.db import get_db


ALLOWED_GROUPS = [
    "České",
    "Rock",
    "Pop",
    "Zprávy",
    "Mluvené",
    "Ostatní",
]


def row_to_dict(row):
    return dict(row) if row else None


def normalize_station_form(form_data: dict) -> dict:
    group_name = form_data.get("group_name", "Ostatní").strip() or "Ostatní"
    if group_name not in ALLOWED_GROUPS:
        group_name = "Ostatní"

    return {
        "name": form_data.get("name", "").strip(),
        "group_name": group_name,
        "stream_url": form_data.get("stream_url", "").strip(),
        "logo_url": form_data.get("logo_url", "").strip(),
        "is_favorite": 1 if form_data.get("is_favorite") else 0,
    }


def is_valid_stream_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def get_all_stations() -> list[dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name, group_name, stream_url, logo_url, is_favorite, sort_order
        FROM stations
        WHERE is_active = 1
        ORDER BY sort_order ASC, name COLLATE NOCASE ASC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_favorite_stations() -> list[dict]:
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name, group_name, stream_url, logo_url, is_favorite, sort_order
        FROM stations
        WHERE is_active = 1 AND is_favorite = 1
        ORDER BY sort_order ASC, name COLLATE NOCASE ASC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_station_by_id(station_id: int) -> dict | None:
    db = get_db()
    row = db.execute(
        """
        SELECT id, name, group_name, stream_url, logo_url, is_favorite, sort_order
        FROM stations
        WHERE id = ?
        """,
        (station_id,),
    ).fetchone()
    return row_to_dict(row)


def validate_station(data: dict, station_id: int | None = None) -> tuple[bool, str | None]:
    if not data["name"]:
        return False, "Vyplň název stanice."

    if len(data["name"]) > 100:
        return False, "Název stanice je příliš dlouhý."

    if not is_valid_stream_url(data["stream_url"]):
        return False, "URL streamu není platná."

    db = get_db()

    if station_id is None:
        row = db.execute(
            "SELECT id FROM stations WHERE stream_url = ?",
            (data["stream_url"],),
        ).fetchone()
    else:
        row = db.execute(
            "SELECT id FROM stations WHERE stream_url = ? AND id != ?",
            (data["stream_url"], station_id),
        ).fetchone()

    if row:
        return False, "Stanice s touto URL už existuje."

    return True, None


def create_station(form_data: dict) -> tuple[bool, str | None]:
    data = normalize_station_form(form_data)
    valid, error = validate_station(data)
    if not valid:
        return False, error

    db = get_db()
    db.execute(
        """
        INSERT INTO stations (name, group_name, stream_url, logo_url, is_favorite)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["name"],
            data["group_name"],
            data["stream_url"],
            data["logo_url"] or None,
            data["is_favorite"],
        ),
    )
    db.commit()
    return True, None


def update_station(station_id: int, form_data: dict) -> tuple[bool, str | None]:
    data = normalize_station_form(form_data)
    valid, error = validate_station(data, station_id=station_id)
    if not valid:
        return False, error

    db = get_db()
    db.execute(
        """
        UPDATE stations
        SET
            name = ?,
            group_name = ?,
            stream_url = ?,
            logo_url = ?,
            is_favorite = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            data["name"],
            data["group_name"],
            data["stream_url"],
            data["logo_url"] or None,
            data["is_favorite"],
            station_id,
        ),
    )
    db.commit()
    return True, None


def delete_station(station_id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM stations WHERE id = ?", (station_id,))
    db.commit()
