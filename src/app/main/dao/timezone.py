import datetime

from ... import db
from ..models.main import Timezone


def get_timezone_with_id(timezone_id):
    return Timezone.query.get(timezone_id)


def get_all_timezones():
    return Timezone.query.all()


def get_timezone_with_name(name):
    return Timezone.query.filter(
        db.func.lower(Timezone.name) == name.strip().lower()
    ).first()


def get_timezone_with_identifier(identifier):
    return Timezone.query.filter(
        Timezone.all_identifiers.contains([identifier])
    ).first()


def create_timezone(name, identifier, other_identifiers):
    now = datetime.datetime.now()
    timezone = Timezone(
        name=name,
        identifier=identifier,
        created_at=now,
        all_identifiers=[identifier] + other_identifiers,
    )
    db.session.add(timezone)
    db.session.flush()

    return timezone
