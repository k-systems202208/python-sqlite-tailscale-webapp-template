"""Removable items sample feature."""


def register(app) -> None:
    from .routes import bp

    app.register_blueprint(bp)
