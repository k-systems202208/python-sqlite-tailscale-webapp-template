from importlib import import_module
from pkgutil import iter_modules


def feature_names() -> list[str]:
    """Return feature packages currently present under app.features."""

    return sorted(module.name for module in iter_modules(__path__) if module.ispkg)


def register_features(app) -> None:
    """Register every feature package that exposes register(app).

    A sample feature can therefore be removed by deleting its package; the
    application factory does not contain feature-specific imports.
    """

    for name in feature_names():
        module = import_module(f"{__name__}.{name}")
        register = getattr(module, "register", None)
        if callable(register):
            register(app)
