from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, request

from .auth import resolve_identity
from .config import load_settings
from .core.routes import bp as core_bp
from .csrf import install_csrf
from .db import close_db, ensure_user, init_db
from .features import register_features
from .security import install_security_headers

HEALTH_PATHS = {"/healthz", "/readyz"}


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(load_settings())

    if test_config:
        app.config.update(test_config)

    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    data_dir = Path(app.config["APP_DATA_DIR"])
    data_dir.mkdir(parents=True, exist_ok=True)

    if not app.config.get("SECRET_KEY"):
        secret_path = data_dir / ".secret_key"
        if not secret_path.exists():
            import secrets

            secret_path.write_text(secrets.token_hex(32), encoding="utf-8")
        app.config["SECRET_KEY"] = secret_path.read_text(encoding="utf-8").strip()

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.before_request
    def load_current_user():
        if request.path in HEALTH_PATHS:
            g.identity = None
            g.current_user = None
            return

        identity = resolve_identity()
        g.identity = identity
        g.current_user = ensure_user(identity) if identity else None

    install_csrf(app)
    install_security_headers(app)
    app.register_blueprint(core_bp)
    register_features(app)

    return app
