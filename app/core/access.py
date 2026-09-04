from functools import wraps

from flask import abort, g


def require_user(view):
    """Require the common resolved application user before running a view."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.current_user is None:
            abort(401)
        return view(*args, **kwargs)

    return wrapped
