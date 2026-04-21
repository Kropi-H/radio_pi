from app import create_app
from app.db import init_db
from app.services.settings_service import set_setting

app = create_app()

with app.app_context():
    init_db()
    set_setting("player.volume", "70")
    set_setting("player.last_station_id", "")
    print("Databáze vytvořena.")
