from flask import g, request

from .. import login_manager
from ..main.dao import session as session_dao
from ..main.dao import user as user_dao
from ..utils.response import unauthorized_error

AUTH_TOKEN_LENGTH = 22


def load_session_and_user_and_permissions():
    """
    Middleware to read authentication token from the request headers
    and load the current session, user and permissions. The current session,
    user and permissions are set in the context global object 'g' as
    'current_session', 'current_user' and 'current_user_permissions' attributes.
    """
    g.current_session = None
    g.current_user = None
    g.current_user_permissions = None

    session = load_session()
    if not session:
        return

    permissions = user_dao.get_user_permission_identifiers(session.user)

    g.current_session = session
    g.current_user = session.user
    g.current_user_permissions = permissions


def load_session():
    auth_token = request.headers.get("Authorization")
    if auth_token and len(auth_token) == AUTH_TOKEN_LENGTH:
        db_session = session_dao.get_session_with_uuid(auth_token)
        if db_session and db_session.is_valid():
            return db_session
    return None


@login_manager.request_loader
def load_user_from_request(_):
    return g.current_user


@login_manager.unauthorized_handler
def unauthorized():
    return unauthorized_error()
