from dataclasses import dataclass
from email.header import decode_header, make_header
from ipaddress import ip_address

from flask import current_app, request


@dataclass(frozen=True)
class Identity:
    login: str
    display_name: str
    source: str


def _is_loopback(value: str | None) -> bool:
    if not value:
        return False
    try:
        return ip_address(value).is_loopback
    except ValueError:
        return False


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def resolve_identity() -> Identity | None:
    """Resolve caller identity without trusting proxy headers from the network."""
    remote_is_loopback = _is_loopback(request.remote_addr)

    ts_login = request.headers.get("Tailscale-User-Login", "").strip()
    if ts_login and remote_is_loopback:
        ts_name = _decode_header(request.headers.get("Tailscale-User-Name")) or ts_login
        return Identity(login=ts_login.lower(), display_name=ts_name, source="tailscale")

    if remote_is_loopback:
        email = current_app.config.get("LOCAL_OWNER_EMAIL", "").strip()
        if email:
            return Identity(
                login=email.lower(),
                display_name=current_app.config.get("LOCAL_OWNER_NAME", "Local Owner"),
                source="local",
            )

        if current_app.config.get("ALLOW_ANONYMOUS"):
            return Identity(
                login="anonymous@localhost", display_name="Anonymous", source="anonymous"
            )

    return None
