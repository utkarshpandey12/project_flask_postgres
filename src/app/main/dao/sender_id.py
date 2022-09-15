import datetime

from ... import db
from ..models.main import SenderId


def get_all_sender_ids_with_org(org):
    return SenderId.query.filter(SenderId.org == org).all()


def get_sender_id_with_id_and_org(sender_id, org):
    return SenderId.query.filter(SenderId.id == sender_id, SenderId.org == org).first()


def get_sender_id_with_value(value):
    return SenderId.query.filter(
        db.func.lower(SenderId.value) == value.strip().lower()
    ).first()


def get_sender_id_with_criteria(org, country, sms_provider):
    return SenderId.query.filter(
        SenderId.org == org,
        SenderId.country == country,
        SenderId.sms_provider == sms_provider,
    ).first()


def create_sender_id(country, sms_provider, value, org, current_user):
    now = datetime.datetime.now()
    sender_id = SenderId(
        country=country,
        sms_provider=sms_provider,
        value=value,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(sender_id)
    db.session.flush()
    return sender_id


def update_sender_id(sender_id, value, current_user):
    now = datetime.datetime.now()
    sender_id.value = value
    sender_id.updated_at = now
    sender_id.updated_by_user = current_user
    return sender_id


def delete_sender_id(sender_id_obj):
    db.session.delete(sender_id_obj)
