import datetime

from ... import db
from ..models.main import CallerId, CallerIdHistory


def get_caller_id_with_id(caller_id, *, org):
    return CallerId.query.filter(CallerId.id == caller_id, CallerId.org == org).first()


def get_caller_ids(*, org):
    return CallerId.query.filter(CallerId.org == org).all()


def get_caller_id_with_phone_no(phone_no, *, for_org):
    org_filter = CallerId.org_id.isnot(None) if for_org else CallerId.org_id.is_(None)
    return CallerId.query.filter(CallerId.phone_no == phone_no, org_filter).first()


def create_caller_id(
    *,
    country,
    telephony_provider,
    call_type=None,
    user=None,
    phone_no,
    org=None,
    current_user,
):
    now = datetime.datetime.now()
    caller_id = CallerId(
        country=country,
        telephony_provider=telephony_provider,
        call_type=call_type,
        user=user,
        phone_no=phone_no,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(caller_id)
    db.session.flush()
    return caller_id


def create_caller_id_history(
    *,
    country,
    telephony_provider,
    call_type=None,
    user=None,
    phone_no,
    action,
    org=None,
    current_user,
):
    now = datetime.datetime.now()
    caller_id_history = CallerIdHistory(
        country=country,
        telephony_provider=telephony_provider,
        call_type=call_type,
        user=user,
        phone_no=phone_no,
        action=action,
        org=org,
        action_at=now,
        action_by_user=current_user,
    )
    db.session.add(caller_id_history)
    db.session.flush()
    return caller_id_history


def update_caller_id(caller_id, phone_no, current_user):
    now = datetime.datetime.now()
    caller_id.phone_no = phone_no
    caller_id.updated_at = now
    caller_id.updated_by_user = current_user
    return caller_id


def delete_caller_id(caller_id_obj):
    db.session.delete(caller_id_obj)
