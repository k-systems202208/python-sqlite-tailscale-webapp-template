from flask import Flask

import app.features as features


def test_items_sample_is_discovered_as_feature():
    assert "items" in features.feature_names()


def test_feature_registration_is_safe_when_no_feature_package_exists(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(features, "feature_names", lambda: [])

    features.register_features(app)

    assert list(app.blueprints) == []
