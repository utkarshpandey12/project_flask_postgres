from ... import db
from ..models.main import Session, User


def get_session_with_uuid(uuid):
    return (
        Session.query.join(User)
        .options(db.contains_eager(Session.user))
        .filter(Session.uuid == uuid)
        .first()
    )
