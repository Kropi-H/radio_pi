from flask import Flask
from pathlib import Path

from app.db import init_app
from app.routes.ui import ui
from app.routes.api_player import api_player
from app.routes.api_system import api_system
from app.services.audio_service import AudioService


def create_app() -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    app.config.from_mapping(
        SECRET_KEY="dev-change-this",
        DATABASE=Path(app.instance_path) / "audio_panel.db",
        PROJECT_ROOT=Path(app.root_path).parent,
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.audio_service = AudioService()

    init_app(app)
    app.register_blueprint(ui)
    app.register_blueprint(api_player)
    app.register_blueprint(api_system)

    return app
