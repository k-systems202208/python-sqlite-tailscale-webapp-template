from ipaddress import ip_address

from waitress import serve

from app import create_app


def _require_loopback(host: str) -> None:
    """Refuse accidental LAN/public exposure by design."""
    try:
        if not ip_address(host).is_loopback:
            raise SystemExit(
                f"Refusing to bind to non-loopback address: {host}. "
                "This template is designed for 127.0.0.1 + Tailscale Serve."
            )
    except ValueError as exc:
        raise SystemExit(f"APP_HOST must be a loopback IP address: {host}") from exc


app = create_app()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = int(app.config["APP_PORT"])
    _require_loopback(host)
    print(f"{app.config['APP_NAME']} listening on http://{host}:{port}")
    print("For tailnet access, run: tailscale serve --bg", port)
    serve(app, host=host, port=port, threads=8)
