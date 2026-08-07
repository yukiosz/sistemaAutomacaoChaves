from flask import Flask
from pathlib import Path
import os

from .database import inicializar_banco


def create_app():
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    # Em produção, defina SECRET_KEY para manter as sessões entre reinicializações.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)

    inicializar_banco()

    from .routes import web

    app.register_blueprint(web)
    return app
