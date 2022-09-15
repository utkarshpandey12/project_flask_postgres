import datetime

from sqlalchemy.exc import IntegrityError

from ... import db
from ..models.main import Language


def get_all_language():
    return Language.query.all()


def get_language_by_id(language_id):
    return Language.query.get(language_id)


def get_language_by_name(name):
    return Language.query.filter(
        db.func.lower(Language.name) == name.strip().lower()
    ).first()


def get_language_by_identifier(identifier):
    return Language.query.filter(
        db.func.lower(Language.identifier) == identifier.strip().lower()
    ).first()


def create_language(name, identifier):
    now = datetime.datetime.now()
    language = Language(name=name, identifier=identifier.upper(), created_at=now)
    db.session.add(language)
    db.session.flush()
    return language


def update_language(language, name, identifier, current_user):
    language.name = name
    language.identifier = identifier
    return language


def delete_language(language):
    try:
        db.session.delete(language)
        db.session.flush()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
