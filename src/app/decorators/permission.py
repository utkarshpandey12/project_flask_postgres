from functools import wraps

from flask import g

from ..utils.response import unauthorized_error


def sys_admin_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user or not g.current_user.is_sys_admin:
                return unauthorized_error()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def _has_permission(permissions, permission_to_check):
    if not permissions:
        return False

    if isinstance(permission_to_check, str):
        return permission_to_check in permissions
    elif (
        isinstance(permission_to_check, list)
        or isinstance(permission_to_check, tuple)
        or isinstance(permission_to_check, set)
    ):
        permissions_to_check = permission_to_check
        for permission in permissions_to_check:
            if permission in permissions:
                return True
    return False


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not _has_permission(g.current_user_permissions, permission):
                return unauthorized_error()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def org_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_org:
                return unauthorized_error()
            return f(*args, **kwargs)

        return decorated_function

    return decorator
