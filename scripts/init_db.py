from pathlib import Path
import sys

# Ensure the project root is importable when this script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.db import init_db
from app.services.settings_service import set_setting

app = create_app()

with app.app_context():
    init_db()
    set_setting("player.volume", "70")
    set_setting("player.last_station_id", "")
    print("Databáze vytvořena.")
